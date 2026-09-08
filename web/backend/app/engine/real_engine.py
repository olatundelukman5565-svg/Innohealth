"""The production :class:`ThermalMeshEngineAdapter` implementation.

Runs the real ``thermalmesh`` Python pipeline (installed from the repo
root) in a background thread pool, translating its stage callbacks into
database updates the API/SSE layer can read. This is not a mock: uploaded
files are actually validated, aligned, projected, and exported by the same
engine documented in ../../../docs/architecture.md.
"""

from __future__ import annotations

import logging
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session, sessionmaker

from app.engine.adapter import EngineInputPaths, ThermalMeshEngineAdapter
from app.engine.stage_mapping import INTERNAL_TO_PUBLIC, PUBLIC_STAGE_ORDER, TOTAL_INTERNAL_STAGES
from app.models.enums import JobStatus, ProcessingStageName, StageStatus
from app.models.processing import ProcessingJob, ProcessingStage

logger = logging.getLogger("thermalmesh.web.engine")

# The default config's uv.resolution (2048) produces per-image thermal
# layer arrays that are enormous relative to a browser-served demo (a
# handful of views at 2048x2048 float64 quickly reaches hundreds of MB per
# project). 512 is still plenty of detail for the small meshes this
# platform demonstrates and keeps storage/response sizes reasonable.
WEB_CONFIG_OVERRIDES = {"uv": {"resolution": 512}}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RealThermalMeshEngine(ThermalMeshEngineAdapter):
    def __init__(self, session_factory: sessionmaker, max_workers: int = 2) -> None:
        self._session_factory = session_factory
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="thermalmesh-job")
        self._cancel_flags: dict[str, threading.Event] = {}

    # ------------------------------------------------------------ validate

    def validate_input(self, inputs: EngineInputPaths) -> list[str]:
        errors: list[str] = []
        if not Path(inputs.mesh_path).exists():
            errors.append("Final mesh file is missing.")
        if not Path(inputs.thermal_dir).exists() or not any(Path(inputs.thermal_dir).iterdir()):
            errors.append("No thermal data files were found.")
        if not Path(inputs.cameras_path).exists():
            errors.append("Camera metadata file is missing.")
        if inputs.initial_mesh_path and not Path(inputs.initial_mesh_path).exists():
            errors.append("Initial mesh file was specified but is missing.")
        return errors

    # -------------------------------------------------------------- start

    def start_processing(self, job_id: str, project_id: str, inputs: EngineInputPaths, output_dir: str) -> None:
        self._cancel_flags[job_id] = threading.Event()
        self._executor.submit(self._run_job, job_id, project_id, inputs, output_dir)

    def _run_job(self, job_id: str, project_id: str, inputs: EngineInputPaths, output_dir: str) -> None:
        from app.engine.persistence import persist_job_failure, persist_job_success  # local import avoids a cycle

        db = self._session_factory()
        try:
            job = db.get(ProcessingJob, job_id)
            if job is None:
                return
            job.status = JobStatus.RUNNING
            job.started_at = _utcnow()
            db.commit()

            completed_internal_by_public: dict[ProcessingStageName, set[str]] = {name: set() for name in PUBLIC_STAGE_ORDER}
            required_internal_by_public: dict[ProcessingStageName, set[str]] = {name: set() for name in PUBLIC_STAGE_ORDER}
            for internal_name, public_names in INTERNAL_TO_PUBLIC.items():
                for public_name in public_names:
                    required_internal_by_public[public_name].add(internal_name)

            def on_stage_start(name: str, index: int, total: int) -> None:
                cancel_flag = self._cancel_flags.get(job_id)
                if cancel_flag is not None and cancel_flag.is_set():
                    raise _CancelledError()
                job_row = db.get(ProcessingJob, job_id)
                for public_name in INTERNAL_TO_PUBLIC.get(name, []):
                    stage_row = _get_stage(db, job_id, public_name)
                    if stage_row and stage_row.status == StageStatus.PENDING:
                        stage_row.status = StageStatus.RUNNING
                        stage_row.started_at = _utcnow()
                    if job_row:
                        job_row.current_stage = public_name
                if job_row:
                    job_row.progress_percent = round((index - 1) / total * 100, 1)
                db.commit()

            def on_stage_complete(name: str, index: int, total: int) -> None:
                for public_name in INTERNAL_TO_PUBLIC.get(name, []):
                    completed_internal_by_public[public_name].add(name)
                    if completed_internal_by_public[public_name] >= required_internal_by_public[public_name]:
                        stage_row = _get_stage(db, job_id, public_name)
                        if stage_row and stage_row.status != StageStatus.COMPLETED:
                            stage_row.status = StageStatus.COMPLETED
                            stage_row.completed_at = _utcnow()
                job_row = db.get(ProcessingJob, job_id)
                if job_row:
                    job_row.progress_percent = round(index / total * 100, 1)
                db.commit()

            camera_dimensions = _load_camera_dimensions(inputs.cameras_path)

            from thermalmesh.pipeline.runner import run_pipeline

            result = run_pipeline(
                mesh_path=inputs.mesh_path,
                thermal_dir=inputs.thermal_dir,
                cameras_path=inputs.cameras_path,
                output_dir=output_dir,
                initial_mesh_path=inputs.initial_mesh_path,
                config_overrides=WEB_CONFIG_OVERRIDES,
                on_stage_start=on_stage_start,
                on_stage_complete=on_stage_complete,
            )

            job = db.get(ProcessingJob, job_id)
            job.status = JobStatus.COMPLETED
            job.completed_at = _utcnow()
            job.progress_percent = 100.0
            job.current_stage = ProcessingStageName.REPORT_GENERATION
            db.commit()

            persist_job_success(db, project_id, output_dir, result, camera_dimensions)

        except _CancelledError:
            job = db.get(ProcessingJob, job_id)
            if job:
                job.status = JobStatus.CANCELLED
                job.completed_at = _utcnow()
                db.commit()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Processing job %s failed", job_id)
            persist_job_failure(db, job_id, project_id, exc, traceback.format_exc())
        finally:
            self._cancel_flags.pop(job_id, None)
            db.close()

    # ------------------------------------------------------------- status

    def get_status(self, job_id: str) -> dict:
        db = self._session_factory()
        try:
            job = db.get(ProcessingJob, job_id)
            if job is None:
                return {}
            return {
                "status": job.status.value,
                "current_stage": job.current_stage.value if job.current_stage else None,
                "progress_percent": job.progress_percent,
            }
        finally:
            db.close()

    def cancel_processing(self, job_id: str) -> bool:
        flag = self._cancel_flags.get(job_id)
        if flag is None:
            return False
        flag.set()
        return True

    def get_result(self, job_id: str) -> dict | None:
        db = self._session_factory()
        try:
            job = db.get(ProcessingJob, job_id)
            if job is None or job.status != JobStatus.COMPLETED:
                return None
            return {"project_id": job.project_id}
        finally:
            db.close()

    def get_quality_report(self, job_id: str) -> dict | None:
        db = self._session_factory()
        try:
            job = db.get(ProcessingJob, job_id)
            if job is None:
                return None
            from app.models.result import ProcessingResult

            result = db.query(ProcessingResult).filter_by(project_id=job.project_id).first()
            return result.quality_report if result else None
        finally:
            db.close()


class _CancelledError(Exception):
    pass


def _get_stage(db: Session, job_id: str, name: ProcessingStageName) -> ProcessingStage | None:
    return db.query(ProcessingStage).filter_by(job_id=job_id, name=name).first()


def _load_camera_dimensions(cameras_path: str) -> dict[str, tuple[int, int]]:
    import json

    with open(cameras_path) as f:
        data = json.load(f)
    return {
        entry["camera_id"]: (entry.get("image_width", 0), entry.get("image_height", 0))
        for entry in data.get("cameras", [])
    }
