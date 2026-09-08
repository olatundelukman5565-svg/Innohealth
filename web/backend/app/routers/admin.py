from __future__ import annotations

import shutil
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.config import settings as app_settings
from app.core.database import get_db
from app.core.deps import require_admin
from app.core.security import hash_password
from app.models.audit import AuditLog
from app.models.enums import AuditAction, JobStatus, ProjectStatus, UserRole
from app.models.processing import ProcessingJob
from app.models.project import Project
from app.models.user import User
from app.schemas.admin import (
    AdminJobOut,
    AdminOverviewOut,
    AdminProjectOut,
    AdminUserCreate,
    AdminUserOut,
    AdminUserUpdate,
    AuditLogOut,
    SystemComponentHealth,
    SystemHealthOut,
)

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])


# ------------------------------------------------------------------ overview

@router.get("/overview", response_model=AdminOverviewOut)
def overview(db: Session = Depends(get_db)) -> AdminOverviewOut:
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_projects = db.query(func.count(Project.id)).filter(
        Project.status.in_([ProjectStatus.PROCESSING, ProjectStatus.QUEUED, ProjectStatus.UPLOADING])
    ).scalar() or 0
    processing_jobs = db.query(func.count(ProcessingJob.id)).filter(
        ProcessingJob.status.in_([JobStatus.QUEUED, JobStatus.RUNNING])
    ).scalar() or 0
    completed_jobs = db.query(func.count(ProcessingJob.id)).filter(ProcessingJob.status == JobStatus.COMPLETED).scalar() or 0
    failed_jobs = db.query(func.count(ProcessingJob.id)).filter(ProcessingJob.status == JobStatus.FAILED).scalar() or 0

    storage_bytes = _directory_size(app_settings.storage_root)

    since = datetime.now(timezone.utc) - timedelta(days=13)
    projects_over_time = _bucket_by_day(
        db.query(Project.created_at).filter(Project.created_at >= since).all(), days=14
    )
    jobs_by_status = [
        {"status": s.value, "count": db.query(func.count(ProcessingJob.id)).filter(ProcessingJob.status == s).scalar() or 0}
        for s in JobStatus
    ]

    recent = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(15).all()

    return AdminOverviewOut(
        total_users=total_users,
        active_projects=active_projects,
        processing_jobs=processing_jobs,
        completed_jobs=completed_jobs,
        failed_jobs=failed_jobs,
        storage_usage_mb=round(storage_bytes / (1024 * 1024), 2),
        projects_over_time=projects_over_time,
        jobs_by_status=jobs_by_status,
        recent_activity=[_audit_out(log, db) for log in recent],
    )


def _directory_size(path) -> int:
    if not path.exists():
        return 0
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def _bucket_by_day(rows, days: int) -> list[dict]:
    today = datetime.now(timezone.utc).date()
    buckets = {(today - timedelta(days=i)): 0 for i in range(days)}
    for (created_at,) in rows:
        day = created_at.date()
        if day in buckets:
            buckets[day] += 1
    return [{"date": day.isoformat(), "count": count} for day, count in sorted(buckets.items())]


def _audit_out(log: AuditLog, db: Session) -> AuditLogOut:
    user = db.get(User, log.user_id) if log.user_id else None
    return AuditLogOut(
        id=log.id, user_email=user.email if user else None, action=log.action,
        project_id=log.project_id, status=log.status, detail=log.detail, created_at=log.created_at,
    )


# --------------------------------------------------------------------- users

@router.get("/users", response_model=list[AdminUserOut])
def list_users(search: str | None = None, db: Session = Depends(get_db)) -> list[AdminUserOut]:
    query = db.query(User)
    if search:
        like = f"%{search.lower()}%"
        query = query.filter((func.lower(User.email).like(like)) | (func.lower(User.full_name).like(like)))
    users = query.order_by(User.created_at.desc()).all()
    counts = dict(db.query(Project.owner_id, func.count(Project.id)).group_by(Project.owner_id).all())
    return [_user_out(u, counts.get(u.id, 0)) for u in users]


def _user_out(user: User, project_count: int) -> AdminUserOut:
    return AdminUserOut(
        id=user.id, email=user.email, full_name=user.full_name, role=user.role,
        is_active=user.is_active, created_at=user.created_at, project_count=project_count,
    )


@router.post("/users", response_model=AdminUserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: AdminUserCreate, db: Session = Depends(get_db)) -> AdminUserOut:
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(status.HTTP_409_CONFLICT, detail="A user with this email already exists")
    user = User(
        email=payload.email.lower(), full_name=payload.full_name,
        hashed_password=hash_password(payload.password), role=payload.role,
    )
    db.add(user)
    db.add(AuditLog(user_id=None, action=AuditAction.USER_CREATED, detail={"email": user.email, "role": user.role.value}))
    db.commit()
    db.refresh(user)
    return _user_out(user, 0)


@router.patch("/users/{user_id}", response_model=AdminUserOut)
def update_user(user_id: str, payload: AdminUserUpdate, db: Session = Depends(get_db)) -> AdminUserOut:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active
    db.add(AuditLog(user_id=None, action=AuditAction.USER_UPDATED, detail={"target_user": user.email}))
    db.commit()
    db.refresh(user)
    count = db.query(func.count(Project.id)).filter(Project.owner_id == user.id).scalar() or 0
    return _user_out(user, count)


# ------------------------------------------------------------------ projects

@router.get("/projects", response_model=list[AdminProjectOut])
def list_all_projects(
    status_filter: ProjectStatus | None = Query(None, alias="status"),
    search: str | None = None,
    db: Session = Depends(get_db),
) -> list[AdminProjectOut]:
    query = db.query(Project)
    if status_filter:
        query = query.filter(Project.status == status_filter)
    if search:
        query = query.filter(func.lower(Project.name).like(f"%{search.lower()}%"))
    projects = query.order_by(Project.updated_at.desc()).all()
    return [
        AdminProjectOut(
            id=p.id, name=p.name, owner_email=p.owner.email if p.owner else "unknown",
            status=p.status, is_demo=p.is_demo, created_at=p.created_at, updated_at=p.updated_at,
        )
        for p in projects
    ]


# ---------------------------------------------------------------------- jobs

@router.get("/jobs", response_model=list[AdminJobOut])
def list_jobs(status_filter: JobStatus | None = Query(None, alias="status"), db: Session = Depends(get_db)) -> list[AdminJobOut]:
    query = db.query(ProcessingJob)
    if status_filter:
        query = query.filter(ProcessingJob.status == status_filter)
    jobs = query.order_by(ProcessingJob.created_at.desc()).limit(200).all()
    return [_job_out(j) for j in jobs]


@router.get("/jobs/{job_id}", response_model=AdminJobOut)
def get_job(job_id: str, db: Session = Depends(get_db)) -> AdminJobOut:
    job = db.get(ProcessingJob, job_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Job not found")
    return _job_out(job)


def _job_out(job: ProcessingJob) -> AdminJobOut:
    duration = None
    if job.started_at and job.completed_at:
        duration = (job.completed_at - job.started_at).total_seconds()
    return AdminJobOut(
        id=job.id, project_id=job.project_id, project_name=job.project.name if job.project else "",
        status=job.status, current_stage=job.current_stage.value if job.current_stage else None,
        progress_percent=job.progress_percent, started_at=job.started_at, completed_at=job.completed_at,
        duration_seconds=duration, error_message=job.error_message, error_detail=job.error_detail,
    )


# --------------------------------------------------------------------- audit

@router.get("/audit", response_model=list[AuditLogOut])
def list_audit_logs(limit: int = Query(100, le=500), db: Session = Depends(get_db)) -> list[AuditLogOut]:
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [_audit_out(log, db) for log in logs]


# -------------------------------------------------------------------- system

@router.get("/system", response_model=SystemHealthOut)
def system_health(db: Session = Depends(get_db)) -> SystemHealthOut:
    components = []

    try:
        db.execute(text("SELECT 1"))  # trivial round-trip
        components.append(SystemComponentHealth(name="Database", status="healthy", detail=app_settings.database_url.split("://")[0]))
    except Exception as exc:  # noqa: BLE001
        components.append(SystemComponentHealth(name="Database", status="error", detail=str(exc)))

    try:
        app_settings.storage_root.mkdir(parents=True, exist_ok=True)
        probe = app_settings.storage_root / ".health_check"
        probe.write_text("ok")
        probe.unlink()
        total, used, free = shutil.disk_usage(app_settings.storage_root)
        pct_free = free / total * 100
        status_value = "healthy" if pct_free > 10 else "warning"
        components.append(SystemComponentHealth(name="Storage", status=status_value, detail=f"{pct_free:.1f}% free"))
    except Exception as exc:  # noqa: BLE001
        components.append(SystemComponentHealth(name="Storage", status="error", detail=str(exc)))

    from app.engine import engine as engine_instance

    worker_count = engine_instance._executor._max_workers  # noqa: SLF001
    components.append(SystemComponentHealth(name="Processing Worker Pool", status="healthy", detail=f"{worker_count} worker thread(s)"))
    components.append(SystemComponentHealth(name="API", status="healthy", detail="FastAPI application responding"))

    return SystemHealthOut(components=components, checked_at=datetime.now(timezone.utc))


@router.get("/settings")
def get_settings() -> dict:
    return {
        "max_upload_mb": app_settings.max_upload_mb,
        "storage_path": str(app_settings.storage_root),
        "cors_origins": app_settings.cors_origin_list,
        "note": "Runtime configuration is managed via environment variables in this version.",
    }
