from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import JobStatus, ProcessingStageName, StageStatus


class ProcessingStageOut(BaseModel):
    name: ProcessingStageName
    sequence: int
    status: StageStatus
    started_at: datetime | None
    completed_at: datetime | None
    metrics: dict

    model_config = {"from_attributes": True}


class ProcessingJobOut(BaseModel):
    id: str
    project_id: str
    status: JobStatus
    current_stage: ProcessingStageName | None
    progress_percent: float
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    stages: list[ProcessingStageOut]

    model_config = {"from_attributes": True}


class ProcessingStartResponse(BaseModel):
    job_id: str
    status: JobStatus
