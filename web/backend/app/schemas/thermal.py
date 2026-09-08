from __future__ import annotations

from pydantic import BaseModel

from app.models.enums import CameraPoseSource


class CameraOut(BaseModel):
    id: str
    camera_key: str
    image_width: int
    image_height: int
    position: list[float]
    rotation: list[list[float]]
    pose_source: CameraPoseSource
    confidence: float
    reprojection_error: float | None
    coverage_percent: float

    model_config = {"from_attributes": True}


class ThermalImageOut(BaseModel):
    id: str
    camera_key: str
    width: int
    height: int
    valid_fraction: float
    min_temperature: float | None
    max_temperature: float | None
    mean_temperature: float | None

    model_config = {"from_attributes": True}


class TemperatureStatistics(BaseModel):
    minimum: float | None
    maximum: float | None
    mean: float | None
    median: float | None
    std: float | None
    coverage_percent: float
    num_vertices: int


class VertexTemperatureRow(BaseModel):
    vertex_id: int
    x: float
    y: float
    z: float
    temperature: float | None
    confidence: float
    observations: int


class VertexTemperaturePage(BaseModel):
    rows: list[VertexTemperatureRow]
    total: int
    page: int
    page_size: int
