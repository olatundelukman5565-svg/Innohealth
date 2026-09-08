"""Translate a completed/failed pipeline run into database rows.

Kept separate from real_engine.py's orchestration logic so the "what do we
store" concerns are easy to read/change independently of the threading and
stage-callback plumbing.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

import numpy as np
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.audit import AuditLog
from app.models.enums import (
    AuditAction,
    CameraPoseSource,
    JobStatus,
    ProjectStatus,
    ReportType,
    StageStatus,
)
from app.models.processing import ProcessingJob, ProcessingStage
from app.models.project import Project
from app.models.result import ProcessingResult, Report
from app.models.thermal import Camera, ThermalImage
from thermalmesh.models.results import PipelineResult
from thermalmesh.pipeline.errors import ThermalMeshError

_POSE_METHOD_TO_SOURCE = {
    "provided": CameraPoseSource.PROVIDED,
    "look_at_init": CameraPoseSource.ESTIMATED,
    "silhouette_bbox_estimation": CameraPoseSource.ESTIMATED,
    "pnp": CameraPoseSource.ESTIMATED,
    "refined_optimization": CameraPoseSource.REFINED,
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _relative_to_storage(path: str) -> str | None:
    try:
        return os.path.relpath(path, settings.storage_root)
    except ValueError:
        return None


def persist_job_success(
    db: Session,
    project_id: str,
    output_dir: str,
    result: PipelineResult,
    camera_dimensions: dict[str, tuple[int, int]],
) -> None:
    metrics = result.quality_metrics or {}
    mesh = result.aligned_mesh

    vertex_temps = result.vertex_temperatures
    finite = vertex_temps[np.isfinite(vertex_temps)] if vertex_temps is not None else np.array([])

    existing = db.query(ProcessingResult).filter_by(project_id=project_id).first()
    if existing is None:
        existing = ProcessingResult(project_id=project_id)
        db.add(existing)

    output_files = result.output_files or {}
    existing.glb_path = _relative_to_storage(output_files["glb"]) if "glb" in output_files else None
    existing.vertex_temperature_path = _relative_to_storage(output_files.get("vertex_temperature_npy", ""))
    existing.face_temperature_path = _relative_to_storage(output_files.get("face_temperature_npy", ""))
    existing.results_json_path = _relative_to_storage(output_files.get("results_json", ""))
    existing.quality_report = _json_safe(metrics)
    existing.num_vertices = mesh.num_vertices if mesh else 0
    existing.num_faces = mesh.num_faces if mesh else 0
    existing.min_temperature = float(finite.min()) if finite.size else None
    existing.max_temperature = float(finite.max()) if finite.size else None
    existing.mean_temperature = float(finite.mean()) if finite.size else None
    existing.median_temperature = float(np.median(finite)) if finite.size else None
    existing.std_temperature = float(finite.std()) if finite.size else None
    existing.coverage_percent = metrics.get("blending", {}).get("final_coverage_percent", 0.0)
    existing.alignment_confidence = metrics.get("registration", {}).get("confidence")
    existing.num_views = len(result.camera_poses or {})

    project = db.get(Project, project_id)
    if project:
        project.status = ProjectStatus.COMPLETED
        project.last_processed_at = _utcnow()

    db.query(Camera).filter_by(project_id=project_id).delete()
    db.query(ThermalImage).filter_by(project_id=project_id).delete()

    thermal_stats = metrics.get("thermal", {})
    projection_stats = metrics.get("projection", {})
    camera_by_key: dict[str, Camera] = {}
    for camera_key, pose in (result.camera_poses or {}).items():
        width, height = camera_dimensions.get(camera_key, (0, 0))
        camera = Camera(
            project_id=project_id,
            camera_key=camera_key,
            image_width=width,
            image_height=height,
            position=list(pose.camera_center),
            rotation=[list(row) for row in pose.rotation],
            pose_source=_POSE_METHOD_TO_SOURCE.get(pose.estimation_method, CameraPoseSource.ESTIMATED),
            confidence=pose.confidence,
            reprojection_error=pose.reprojection_error,
            coverage_percent=projection_stats.get(camera_key, {}).get("coverage_percent", 0.0),
        )
        db.add(camera)
        camera_by_key[camera_key] = camera

    db.flush()  # assign camera IDs before linking thermal images

    for camera_key, stats in thermal_stats.items():
        width, height = camera_dimensions.get(camera_key, (0, 0))
        camera = camera_by_key.get(camera_key)
        db.add(
            ThermalImage(
                project_id=project_id,
                camera_id=camera.id if camera else None,
                camera_key=camera_key,
                width=width,
                height=height,
                valid_fraction=(stats.get("valid_pixels", 0) / max(stats.get("valid_pixels", 0) + stats.get("invalid_pixels", 0), 1)),
                min_temperature=stats.get("min"),
                max_temperature=stats.get("max"),
                mean_temperature=stats.get("mean"),
            )
        )

    db.query(Report).filter_by(project_id=project_id).delete()
    db.add(Report(project_id=project_id, type=ReportType.QUALITY, summary=_json_safe(metrics)))
    db.add(
        Report(
            project_id=project_id,
            type=ReportType.THERMAL_ANALYSIS,
            summary=_json_safe({"thermal": thermal_stats, "blending": metrics.get("blending", {})}),
        )
    )
    db.add(
        Report(
            project_id=project_id,
            type=ReportType.PROCESSING,
            summary=_json_safe(
                {
                    "mesh": metrics.get("mesh", {}),
                    "registration": metrics.get("registration", {}),
                    "camera_poses": {k: v.to_dict() for k, v in (result.camera_poses or {}).items()},
                }
            ),
        )
    )

    db.add(
        AuditLog(
            user_id=None,
            action=AuditAction.PROCESSING_COMPLETED,
            project_id=project_id,
            status="SUCCESS",
            detail={"num_views": existing.num_views, "coverage_percent": existing.coverage_percent},
        )
    )
    db.commit()


def persist_job_failure(db: Session, job_id: str, project_id: str, exc: Exception, traceback_text: str) -> None:
    job = db.get(ProcessingJob, job_id)
    if job:
        job.status = JobStatus.FAILED
        job.completed_at = _utcnow()
        job.error_message = _user_safe_message(exc)
        job.error_detail = traceback_text

        running_stage = (
            db.query(ProcessingStage)
            .filter_by(job_id=job_id, status=StageStatus.RUNNING)
            .first()
        )
        if running_stage:
            running_stage.status = StageStatus.FAILED
            running_stage.completed_at = _utcnow()

    project = db.get(Project, project_id)
    if project:
        project.status = ProjectStatus.FAILED

    db.add(
        AuditLog(
            user_id=None,
            action=AuditAction.PROCESSING_FAILED,
            project_id=project_id,
            status="FAILURE",
            detail={"message": _user_safe_message(exc)},
        )
    )
    db.commit()


def _user_safe_message(exc: Exception) -> str:
    if isinstance(exc, ThermalMeshError):
        return str(exc)
    return "Processing failed due to an internal error. An administrator has been notified."


def _json_safe(value):
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, np.bool_):
        return bool(value)
    return value
