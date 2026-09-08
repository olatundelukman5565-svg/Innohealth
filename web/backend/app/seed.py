"""One-time demo data seeding.

Creates a default admin account, a demo user account, and three demo
projects. The demo projects are not fabricated numbers: a real synthetic
dataset (known 3D geometry, known analytic temperature field, ray-cast
thermal images -- see thermalmesh/synthetic.py) is generated for each and
run through the actual ThermalMesh pipeline via the same code path a real
upload would take, so the numbers in the UI are genuinely computed. They
are still clearly marked ``is_demo=True`` and must never be presented as
real Innohealth measurements.
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.core.storage import storage
from app.engine.adapter import EngineInputPaths
from app.engine.stage_mapping import PUBLIC_STAGE_ORDER
from app.models.enums import ProjectFileType, ProjectStatus, StageStatus, UploadStatus, UserRole
from app.models.processing import ProcessingJob, ProcessingStage
from app.models.project import Project
from app.models.project_file import ProjectFile
from app.models.user import User

logger = logging.getLogger("thermalmesh.web.seed")

ADMIN_EMAIL = "admin@innohealth.com"
ADMIN_PASSWORD = "admin123"  # noqa: S105 -- intentionally documented demo credential, see web/README.md
DEMO_EMAIL = "demo@innohealth.com"
DEMO_PASSWORD = "demo1234"  # noqa: S105

DEMO_PROJECTS = [
    {"name": "Thermal Scan Alpha", "description": "Synthetic validation scan -- 12 views, spherical test geometry.", "num_views": 12, "seed": 1},
    {"name": "Thermal Scan Beta", "description": "Synthetic validation scan -- 8 views, reduced camera coverage.", "num_views": 8, "seed": 2},
    {"name": "Thermal Scan Gamma", "description": "Synthetic validation scan -- 10 views, higher mesh resolution.", "num_views": 10, "seed": 3},
]


def seed_demo_data(db: Session) -> None:
    admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if admin is None:
        admin = User(email=ADMIN_EMAIL, full_name="Innohealth Admin", hashed_password=hash_password(ADMIN_PASSWORD), role=UserRole.ADMIN)
        db.add(admin)

    demo_user = db.query(User).filter(User.email == DEMO_EMAIL).first()
    if demo_user is None:
        demo_user = User(email=DEMO_EMAIL, full_name="Demo User", hashed_password=hash_password(DEMO_PASSWORD), role=UserRole.USER)
        db.add(demo_user)
    db.commit()
    db.refresh(demo_user)

    existing_demo_projects = db.query(Project).filter(Project.owner_id == demo_user.id, Project.is_demo.is_(True)).count()
    if existing_demo_projects >= len(DEMO_PROJECTS):
        return

    logger.info("Seeding demo projects (first run only) -- this runs the real pipeline and takes a little while...")
    for spec in DEMO_PROJECTS:
        try:
            _seed_project(db, demo_user.id, spec)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to seed demo project %s", spec["name"])


def _seed_project(db: Session, owner_id: str, spec: dict) -> None:
    from thermalmesh.synthetic import generate_synthetic_dataset

    project = Project(owner_id=owner_id, name=spec["name"], description=spec["description"], status=ProjectStatus.QUEUED, is_demo=True)
    db.add(project)
    db.flush()

    mesh_dir = storage.path_for(f"projects/{project.id}/mesh")
    thermal_dir = storage.path_for(f"projects/{project.id}/thermal")
    cameras_dir = storage.path_for(f"projects/{project.id}/cameras")
    for d in (mesh_dir, thermal_dir, cameras_dir):
        d.mkdir(parents=True, exist_ok=True)

    generate_synthetic_dataset(
        storage.path_for(f"projects/{project.id}/_generated"),
        num_views=spec["num_views"], seed=spec["seed"], image_width=96, image_height=72, subdivisions=2,
    )
    generated = storage.path_for(f"projects/{project.id}/_generated")

    (generated / "final_mesh.ply").rename(mesh_dir / "final_mesh.ply")
    (generated / "initial_mesh.ply").rename(mesh_dir / "initial_mesh.ply")
    (generated / "cameras.json").rename(cameras_dir / "cameras.json")
    for thermal_file in (generated / "thermal").glob("*.csv"):
        thermal_file.rename(thermal_dir / thermal_file.name)
    (generated / "ground_truth.json").unlink(missing_ok=True)
    (generated / "thermal").rmdir()
    generated.rmdir()

    def _register(filename: str, file_type: ProjectFileType, key: str) -> None:
        path = storage.path_for(key)
        db.add(
            ProjectFile(
                project_id=project.id, filename=filename, type=file_type, size=path.stat().st_size,
                path=key, hash="seed", upload_status=UploadStatus.VALIDATED,
            )
        )

    _register("final_mesh.ply", ProjectFileType.FINAL_MESH, f"projects/{project.id}/mesh/final_mesh.ply")
    _register("initial_mesh.ply", ProjectFileType.INITIAL_MESH, f"projects/{project.id}/mesh/initial_mesh.ply")
    _register("cameras.json", ProjectFileType.CAMERA_METADATA, f"projects/{project.id}/cameras/cameras.json")
    for thermal_file in sorted(thermal_dir.glob("*.csv")):
        _register(thermal_file.name, ProjectFileType.THERMAL_DATA, f"projects/{project.id}/thermal/{thermal_file.name}")

    job = ProcessingJob(project_id=project.id)
    db.add(job)
    db.flush()
    for sequence, stage_name in enumerate(PUBLIC_STAGE_ORDER):
        db.add(ProcessingStage(job_id=job.id, name=stage_name, sequence=sequence, status=StageStatus.PENDING))
    db.commit()

    inputs = EngineInputPaths(
        mesh_path=str(mesh_dir / "final_mesh.ply"),
        thermal_dir=str(thermal_dir),
        cameras_path=str(cameras_dir / "cameras.json"),
        initial_mesh_path=str(mesh_dir / "initial_mesh.ply"),
    )
    output_dir = str(storage.path_for(f"projects/{project.id}/output"))

    from app.engine import engine as engine_instance

    # Run inline (not through the thread pool) so seeding blocks startup
    # until each demo project is genuinely processed by the real engine.
    engine_instance._run_job(job.id, project.id, inputs, output_dir)  # noqa: SLF001
    logger.info("Seeded demo project '%s'", project.name)
