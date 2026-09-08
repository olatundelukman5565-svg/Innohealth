from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import IdMixin, TimestampMixin
from app.models.enums import ProjectStatus


class Project(Base, IdMixin, TimestampMixin):
    __tablename__ = "projects"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    last_processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    owner: Mapped["User"] = relationship(back_populates="projects")  # noqa: F821
    files: Mapped[list["ProjectFile"]] = relationship(back_populates="project", cascade="all, delete-orphan")  # noqa: F821
    jobs: Mapped[list["ProcessingJob"]] = relationship(back_populates="project", cascade="all, delete-orphan")  # noqa: F821
    cameras: Mapped[list["Camera"]] = relationship(back_populates="project", cascade="all, delete-orphan")  # noqa: F821
    thermal_images: Mapped[list["ThermalImage"]] = relationship(back_populates="project", cascade="all, delete-orphan")  # noqa: F821
    result: Mapped["ProcessingResult | None"] = relationship(back_populates="project", uselist=False, cascade="all, delete-orphan")  # noqa: F821
    reports: Mapped[list["Report"]] = relationship(back_populates="project", cascade="all, delete-orphan")  # noqa: F821
