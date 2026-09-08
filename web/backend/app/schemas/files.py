from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ProjectFileType, UploadStatus


class ProjectFileOut(BaseModel):
    id: str
    filename: str
    type: ProjectFileType
    size: int
    upload_status: UploadStatus
    created_at: datetime

    model_config = {"from_attributes": True}
