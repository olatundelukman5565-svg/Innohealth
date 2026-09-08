from __future__ import annotations

from sqlalchemy import Enum, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import IdMixin
from app.models.enums import CameraPoseSource


class Camera(Base, IdMixin):
    __tablename__ = "cameras"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    camera_key: Mapped[str] = mapped_column(String(100))  # e.g. "cam_00"
    image_width: Mapped[int] = mapped_column(Integer)
    image_height: Mapped[int] = mapped_column(Integer)
    position: Mapped[list[float]] = mapped_column(JSON)  # [x, y, z]
    rotation: Mapped[list[list[float]]] = mapped_column(JSON)  # 3x3
    pose_source: Mapped[CameraPoseSource] = mapped_column(Enum(CameraPoseSource))
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    reprojection_error: Mapped[float | None] = mapped_column(Float, nullable=True)
    coverage_percent: Mapped[float] = mapped_column(Float, default=0.0)

    project: Mapped["Project"] = relationship(back_populates="cameras")  # noqa: F821
    thermal_image: Mapped["ThermalImage | None"] = relationship(back_populates="camera", uselist=False)


class ThermalImage(Base, IdMixin):
    __tablename__ = "thermal_images"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    camera_id: Mapped[str | None] = mapped_column(ForeignKey("cameras.id"), nullable=True)
    camera_key: Mapped[str] = mapped_column(String(100))
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    valid_fraction: Mapped[float] = mapped_column(Float, default=0.0)
    min_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    mean_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    visualization_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="thermal_images")  # noqa: F821
    camera: Mapped["Camera | None"] = relationship(back_populates="thermal_image")
