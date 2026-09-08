from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ReportType


class ProcessingResultOut(BaseModel):
    num_vertices: int
    num_faces: int
    min_temperature: float | None
    max_temperature: float | None
    mean_temperature: float | None
    median_temperature: float | None
    std_temperature: float | None
    coverage_percent: float
    alignment_confidence: float | None
    num_views: int
    quality_report: dict
    model_url: str | None  # relative API path to fetch the GLB
    is_synthetic: bool

    model_config = {"from_attributes": True}


class ReportOut(BaseModel):
    id: str
    type: ReportType
    generated_at: datetime
    summary: dict

    model_config = {"from_attributes": True}
