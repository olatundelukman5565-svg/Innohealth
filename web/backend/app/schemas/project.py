from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ProjectStatus


class ProjectCreate(BaseModel):
    name: str
    description: str = ""


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None


class ProjectSummary(BaseModel):
    id: str
    name: str
    description: str
    status: ProjectStatus
    is_demo: bool
    created_at: datetime
    updated_at: datetime
    last_processed_at: datetime | None
    num_views: int = 0
    coverage_percent: float | None = None
    min_temperature: float | None = None
    max_temperature: float | None = None
    has_result: bool = False

    model_config = {"from_attributes": True}


class ProjectDetail(ProjectSummary):
    owner_id: str
