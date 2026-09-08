from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import IdMixin, TimestampMixin, utcnow
from app.models.enums import ReportType


class ProcessingResult(Base, IdMixin, TimestampMixin):
    __tablename__ = "processing_results"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), unique=True)
    glb_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    vertex_temperature_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    face_temperature_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    results_json_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    quality_report: Mapped[dict] = mapped_column(JSON, default=dict)

    num_vertices: Mapped[int] = mapped_column(Integer, default=0)
    num_faces: Mapped[int] = mapped_column(Integer, default=0)
    min_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    mean_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    median_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    std_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    coverage_percent: Mapped[float] = mapped_column(Float, default=0.0)
    alignment_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    num_views: Mapped[int] = mapped_column(Integer, default=0)

    project: Mapped["Project"] = relationship(back_populates="result")  # noqa: F821


class Report(Base, IdMixin):
    __tablename__ = "reports"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    type: Mapped[ReportType] = mapped_column(Enum(ReportType))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    summary: Mapped[dict] = mapped_column(JSON, default=dict)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="reports")  # noqa: F821
