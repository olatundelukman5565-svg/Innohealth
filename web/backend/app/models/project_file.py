from __future__ import annotations

from sqlalchemy import BigInteger, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import IdMixin, TimestampMixin
from app.models.enums import ProjectFileType, UploadStatus


class ProjectFile(Base, IdMixin, TimestampMixin):
    __tablename__ = "project_files"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    filename: Mapped[str] = mapped_column(String(500))
    type: Mapped[ProjectFileType] = mapped_column(Enum(ProjectFileType))
    size: Mapped[int] = mapped_column(BigInteger)
    path: Mapped[str] = mapped_column(String(1000))  # storage-relative key, never an absolute host path
    hash: Mapped[str] = mapped_column(String(64))  # sha256
    upload_status: Mapped[UploadStatus] = mapped_column(Enum(UploadStatus), default=UploadStatus.UPLOADED)

    project: Mapped["Project"] = relationship(back_populates="files")  # noqa: F821
