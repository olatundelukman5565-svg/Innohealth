from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.enums import AuditAction, JobStatus, ProjectStatus, UserRole


class AdminUserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    project_count: int = 0

    model_config = {"from_attributes": True}


class AdminUserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.USER


class AdminUserUpdate(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class AdminProjectOut(BaseModel):
    id: str
    name: str
    owner_email: str
    status: ProjectStatus
    is_demo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminJobOut(BaseModel):
    id: str
    project_id: str
    project_name: str
    status: JobStatus
    current_stage: str | None
    progress_percent: float
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: float | None
    error_message: str | None
    error_detail: str | None

    model_config = {"from_attributes": True}


class AuditLogOut(BaseModel):
    id: str
    user_email: str | None
    action: AuditAction
    project_id: str | None
    status: str
    detail: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class SystemComponentHealth(BaseModel):
    name: str
    status: str  # "healthy" | "warning" | "error"
    detail: str


class SystemHealthOut(BaseModel):
    components: list[SystemComponentHealth]
    checked_at: datetime


class AdminOverviewOut(BaseModel):
    total_users: int
    active_projects: int
    processing_jobs: int
    completed_jobs: int
    failed_jobs: int
    storage_usage_mb: float
    projects_over_time: list[dict]
    jobs_by_status: list[dict]
    recent_activity: list[AuditLogOut]
