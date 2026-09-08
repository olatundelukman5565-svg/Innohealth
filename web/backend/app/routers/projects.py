from __future__ import annotations

import csv
import io
import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_user_via_header_or_query
from app.core.storage import StorageError, storage
from app.core.validation import UploadValidationError, validate_upload
from app.engine import engine
from app.engine.adapter import EngineInputPaths
from app.engine.stage_mapping import PUBLIC_STAGE_ORDER
from app.models.audit import AuditLog
from app.models.enums import (
    AuditAction,
    JobStatus,
    ProjectFileType,
    ProjectStatus,
    StageStatus,
    UploadStatus,
    UserRole,
)
from app.models.processing import ProcessingJob, ProcessingStage
from app.models.project import Project
from app.models.project_file import ProjectFile
from app.models.result import ProcessingResult, Report
from app.models.thermal import Camera, ThermalImage
from app.models.user import User
from app.schemas.files import ProjectFileOut
from app.schemas.processing import ProcessingJobOut, ProcessingStartResponse
from app.schemas.project import ProjectCreate, ProjectDetail, ProjectSummary, ProjectUpdate
from app.schemas.result import ProcessingResultOut, ReportOut
from app.schemas.thermal import CameraOut, TemperatureStatistics, ThermalImageOut, VertexTemperaturePage, VertexTemperatureRow

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _get_owned_project(project_id: str, db: Session, user: User) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You do not have access to this project")
    return project


def _summary(project: Project) -> ProjectSummary:
    result = project.result
    return ProjectSummary(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        is_demo=project.is_demo,
        created_at=project.created_at,
        updated_at=project.updated_at,
        last_processed_at=project.last_processed_at,
        num_views=result.num_views if result else 0,
        coverage_percent=result.coverage_percent if result else None,
        min_temperature=result.min_temperature if result else None,
        max_temperature=result.max_temperature if result else None,
        has_result=result is not None,
    )


@router.get("", response_model=list[ProjectSummary])
def list_projects(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ProjectSummary]:
    projects = db.query(Project).filter(Project.owner_id == user.id).order_by(Project.updated_at.desc()).all()
    return [_summary(p) for p in projects]


@router.post("", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Project:
    project = Project(owner_id=user.id, name=payload.name, description=payload.description, status=ProjectStatus.DRAFT)
    db.add(project)
    db.flush()
    db.add(AuditLog(user_id=user.id, action=AuditAction.PROJECT_CREATED, project_id=project.id, detail={"name": project.name}))
    db.commit()
    db.refresh(project)
    return ProjectDetail(**_summary(project).model_dump(), owner_id=project.owner_id)


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProjectDetail:
    project = _get_owned_project(project_id, db, user)
    return ProjectDetail(**_summary(project).model_dump(), owner_id=project.owner_id)


@router.put("/{project_id}", response_model=ProjectDetail)
def update_project(
    project_id: str, payload: ProjectUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ProjectDetail:
    project = _get_owned_project(project_id, db, user)
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    if payload.status is not None:
        project.status = payload.status
    db.add(AuditLog(user_id=user.id, action=AuditAction.PROJECT_UPDATED, project_id=project.id, detail={}))
    db.commit()
    db.refresh(project)
    return ProjectDetail(**_summary(project).model_dump(), owner_id=project.owner_id)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    project = _get_owned_project(project_id, db, user)
    storage.delete_prefix(f"projects/{project.id}")
    db.add(AuditLog(user_id=user.id, action=AuditAction.PROJECT_DELETED, project_id=project.id, detail={"name": project.name}))
    db.delete(project)
    db.commit()


# --------------------------------------------------------------- file upload

_TYPE_STORAGE_DIR = {
    ProjectFileType.FINAL_MESH: "mesh",
    ProjectFileType.INITIAL_MESH: "mesh",
    ProjectFileType.THERMAL_DATA: "thermal",
    ProjectFileType.THERMAL_IMAGE: "thermal",
    ProjectFileType.CAMERA_METADATA: "cameras",
}


@router.get("/{project_id}/files", response_model=list[ProjectFileOut])
def list_files(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ProjectFile]:
    project = _get_owned_project(project_id, db, user)
    return db.query(ProjectFile).filter_by(project_id=project.id).order_by(ProjectFile.created_at.desc()).all()


@router.post("/{project_id}/upload", response_model=ProjectFileOut, status_code=status.HTTP_201_CREATED)
def upload_file(
    project_id: str,
    file: UploadFile = File(...),
    file_type: ProjectFileType = Form(..., alias="type"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectFile:
    project = _get_owned_project(project_id, db, user)

    file.file.seek(0, io.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)

    try:
        validate_upload(file.filename or "", file_type, size)
    except UploadValidationError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": str(exc), "reason": exc.reason}) from exc

    subdir = _TYPE_STORAGE_DIR[file_type]
    key = f"projects/{project.id}/{subdir}/{file.filename}"
    try:
        written_size, digest = storage.save(key, file.file)
    except StorageError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    record = ProjectFile(
        project_id=project.id, filename=file.filename or "upload", type=file_type,
        size=written_size, path=key, hash=digest, upload_status=UploadStatus.UPLOADED,
    )
    db.add(record)
    if project.status == ProjectStatus.DRAFT:
        project.status = ProjectStatus.UPLOADING
    db.add(
        AuditLog(
            user_id=user.id, action=AuditAction.FILE_UPLOADED, project_id=project.id,
            detail={"filename": file.filename, "type": file_type.value, "size": written_size},
        )
    )
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{project_id}/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(project_id: str, file_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    project = _get_owned_project(project_id, db, user)
    record = db.query(ProjectFile).filter_by(id=file_id, project_id=project.id).first()
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="File not found")
    storage.delete_prefix(record.path)
    db.delete(record)
    db.commit()


# ----------------------------------------------------------------- processing

@router.post("/{project_id}/process", response_model=ProcessingStartResponse, status_code=status.HTTP_202_ACCEPTED)
def start_processing(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProcessingStartResponse:
    project = _get_owned_project(project_id, db, user)
    files = db.query(ProjectFile).filter_by(project_id=project.id).all()

    final_mesh = next((f for f in files if f.type == ProjectFileType.FINAL_MESH), None)
    initial_mesh = next((f for f in files if f.type == ProjectFileType.INITIAL_MESH), None)
    camera_file = next((f for f in files if f.type == ProjectFileType.CAMERA_METADATA), None)
    thermal_files = [f for f in files if f.type == ProjectFileType.THERMAL_DATA]

    missing = []
    if final_mesh is None:
        missing.append("final mesh (.ply)")
    if camera_file is None:
        missing.append("camera metadata (.json)")
    if not thermal_files:
        missing.append("thermal data files")
    if missing:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start processing: missing {', '.join(missing)}. Upload every required file first.",
        )

    inputs = EngineInputPaths(
        mesh_path=str(storage.path_for(final_mesh.path)),
        thermal_dir=str(storage.path_for(f"projects/{project.id}/thermal")),
        cameras_path=str(storage.path_for(camera_file.path)),
        initial_mesh_path=str(storage.path_for(initial_mesh.path)) if initial_mesh else None,
    )
    errors = engine.validate_input(inputs)
    if errors:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="; ".join(errors))

    job = ProcessingJob(project_id=project.id, status=JobStatus.QUEUED)
    db.add(job)
    db.flush()
    for sequence, stage_name in enumerate(PUBLIC_STAGE_ORDER):
        db.add(ProcessingStage(job_id=job.id, name=stage_name, sequence=sequence, status=StageStatus.PENDING))

    project.status = ProjectStatus.PROCESSING
    db.add(AuditLog(user_id=user.id, action=AuditAction.PROCESSING_STARTED, project_id=project.id, detail={"job_id": job.id}))
    db.commit()

    output_dir = str(storage.path_for(f"projects/{project.id}/output"))
    engine.start_processing(job.id, project.id, inputs, output_dir)

    return ProcessingStartResponse(job_id=job.id, status=JobStatus.QUEUED)


def _latest_job(project_id: str, db: Session) -> ProcessingJob | None:
    return (
        db.query(ProcessingJob)
        .filter_by(project_id=project_id)
        .order_by(ProcessingJob.created_at.desc())
        .first()
    )


@router.get("/{project_id}/processing", response_model=ProcessingJobOut)
def get_processing_status(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProcessingJob:
    project = _get_owned_project(project_id, db, user)
    job = _latest_job(project.id, db)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No processing job has been started for this project")
    return job


@router.post("/{project_id}/processing/cancel")
def cancel_processing(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    project = _get_owned_project(project_id, db, user)
    job = _latest_job(project.id, db)
    if job is None or job.status not in (JobStatus.QUEUED, JobStatus.RUNNING):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No active processing job to cancel")
    cancelled = engine.cancel_processing(job.id)
    return {"cancelled": cancelled}


@router.get("/{project_id}/processing/stream")
async def stream_processing_status(project_id: str, token: str, db: Session = Depends(get_db)):
    """Server-sent events of processing progress.

    Auth token comes as a query parameter (``?token=...``) because
    ``EventSource`` cannot set an Authorization header.
    """
    import asyncio

    from fastapi import HTTPException as _HTTPException
    from sse_starlette.sse import EventSourceResponse

    from app.core.security import decode_access_token

    try:
        payload = decode_access_token(token)
    except Exception as exc:  # noqa: BLE001
        raise _HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    user = db.get(User, payload.get("sub"))
    if user is None:
        raise _HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    project = _get_owned_project(project_id, db, user)

    async def event_generator():
        last_payload = None
        for _ in range(600):  # ~5 minutes at 0.5s polling, well beyond expected demo processing time
            from app.core.database import SessionLocal

            poll_db = SessionLocal()
            try:
                job = _latest_job(project.id, poll_db)
                if job is None:
                    yield {"event": "error", "data": json.dumps({"message": "No job found"})}
                    return
                data = ProcessingJobOut.model_validate(job).model_dump(mode="json")
                serialized = json.dumps(data)
                if serialized != last_payload:
                    yield {"event": "update", "data": serialized}
                    last_payload = serialized
                if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                    yield {"event": "done", "data": serialized}
                    return
            finally:
                poll_db.close()
            await asyncio.sleep(0.5)

    return EventSourceResponse(event_generator())


# --------------------------------------------------------------------- results

@router.get("/{project_id}/results", response_model=ProcessingResultOut)
def get_results(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProcessingResultOut:
    project = _get_owned_project(project_id, db, user)
    result = db.query(ProcessingResult).filter_by(project_id=project.id).first()
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No results yet -- processing has not completed")
    return ProcessingResultOut(
        num_vertices=result.num_vertices, num_faces=result.num_faces,
        min_temperature=result.min_temperature, max_temperature=result.max_temperature,
        mean_temperature=result.mean_temperature, median_temperature=result.median_temperature,
        std_temperature=result.std_temperature, coverage_percent=result.coverage_percent,
        alignment_confidence=result.alignment_confidence, num_views=result.num_views,
        quality_report=result.quality_report,
        model_url=f"/api/projects/{project.id}/model.glb" if result.glb_path else None,
        is_synthetic=project.is_demo,
    )


@router.get("/{project_id}/model.glb")
def get_model(project_id: str, user: User = Depends(get_current_user_via_header_or_query), db: Session = Depends(get_db)):
    project = _get_owned_project(project_id, db, user)
    result = db.query(ProcessingResult).filter_by(project_id=project.id).first()
    if result is None or not result.glb_path:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="3D model is not available for this project yet")
    path = storage.path_for(result.glb_path)
    if not path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="3D model file is missing from storage")
    return FileResponse(path, media_type="model/gltf-binary", filename="model.glb")


_DOWNLOAD_ARTIFACTS = {
    "vertex_temperature": ("vertex_temperature_path", "application/octet-stream", "vertex_temperature.npy"),
    "face_temperature": ("face_temperature_path", "application/octet-stream", "face_temperature.npy"),
    "results_json": ("results_json_path", "application/json", "results.json"),
}


@router.get("/{project_id}/download/{artifact}")
def download_artifact(
    project_id: str, artifact: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    project = _get_owned_project(project_id, db, user)
    if artifact == "temperatures_csv":
        path = storage.path_for(f"projects/{project.id}/output/data/temperatures.csv")
        if not path.exists():
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Temperature CSV is not available for this project yet")
        return FileResponse(path, media_type="text/csv", filename="temperatures.csv")

    spec = _DOWNLOAD_ARTIFACTS.get(artifact)
    if spec is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Unknown artifact '{artifact}'")
    field, media_type, filename = spec
    result = db.query(ProcessingResult).filter_by(project_id=project.id).first()
    stored_path = getattr(result, field, None) if result else None
    if not stored_path:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{filename} is not available for this project yet")
    path = storage.path_for(stored_path)
    if not path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{filename} is missing from storage")
    return FileResponse(path, media_type=media_type, filename=filename)


@router.get("/{project_id}/thermal", response_model=list[ThermalImageOut])
def list_thermal(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ThermalImage]:
    project = _get_owned_project(project_id, db, user)
    return db.query(ThermalImage).filter_by(project_id=project.id).order_by(ThermalImage.camera_key).all()


@router.get("/{project_id}/cameras", response_model=list[CameraOut])
def list_cameras(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Camera]:
    project = _get_owned_project(project_id, db, user)
    return db.query(Camera).filter_by(project_id=project.id).order_by(Camera.camera_key).all()


@router.get("/{project_id}/temperature", response_model=VertexTemperaturePage)
def get_temperature_data(
    project_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    min_temperature: float | None = None,
    max_temperature: float | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VertexTemperaturePage:
    project = _get_owned_project(project_id, db, user)
    candidate = storage.path_for(f"projects/{project.id}/output/data/temperatures.csv")
    if not candidate.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Temperature data is not available for this project yet")

    rows: list[VertexTemperatureRow] = []
    with candidate.open() as f:
        reader = csv.DictReader(f)
        for raw in reader:
            temperature = float(raw["temperature"]) if raw["temperature"] else None
            if min_temperature is not None and (temperature is None or temperature < min_temperature):
                continue
            if max_temperature is not None and (temperature is None or temperature > max_temperature):
                continue
            rows.append(
                VertexTemperatureRow(
                    vertex_id=int(raw["vertex_id"]), x=float(raw["x"]), y=float(raw["y"]), z=float(raw["z"]),
                    temperature=temperature, confidence=float(raw["confidence"]), observations=int(raw["observation_count"]),
                )
            )

    total = len(rows)
    start = (page - 1) * page_size
    page_rows = rows[start : start + page_size]
    return VertexTemperaturePage(rows=page_rows, total=total, page=page, page_size=page_size)


@router.get("/{project_id}/reports", response_model=list[ReportOut])
def list_reports(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Report]:
    project = _get_owned_project(project_id, db, user)
    return db.query(Report).filter_by(project_id=project.id).all()


@router.get("/{project_id}/reports/{report_id}", response_model=ReportOut)
def get_report(project_id: str, report_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Report:
    project = _get_owned_project(project_id, db, user)
    report = db.query(Report).filter_by(id=report_id, project_id=project.id).first()
    if report is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report
