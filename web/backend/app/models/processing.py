from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import IdMixin, TimestampMixin
from app.models.enums import JobStatus, ProcessingStageName, StageStatus


class ProcessingJob(Base, IdMixin, TimestampMixin):
    __tablename__ = "processing_jobs"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.QUEUED)
    current_stage: Mapped[ProcessingStageName | None] = mapped_column(Enum(ProcessingStageName), nullable=True)
    progress_percent: Mapped[float] = mapped_column(Float, default=0.0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_detail: Mapped[str | None] = mapped_column(Text, nullable=True)  # internal only, never sent to non-admin users

    project: Mapped["Project"] = relationship(back_populates="jobs")  # noqa: F821
    stages: Mapped[list["ProcessingStage"]] = relationship(back_populates="job", cascade="all, delete-orphan", order_by="ProcessingStage.sequence")


class ProcessingStage(Base, IdMixin):
    __tablename__ = "processing_stages"

    job_id: Mapped[str] = mapped_column(ForeignKey("processing_jobs.id"))
    name: Mapped[ProcessingStageName] = mapped_column(Enum(ProcessingStageName))
    sequence: Mapped[int] = mapped_column(Integer)
    status: Mapped[StageStatus] = mapped_column(Enum(StageStatus), default=StageStatus.PENDING)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)

    job: Mapped["ProcessingJob"] = relationship(back_populates="stages")
