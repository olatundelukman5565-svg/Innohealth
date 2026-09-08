from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import IdMixin, TimestampMixin
from app.models.enums import AuditAction


class AuditLog(Base, IdMixin, TimestampMixin):
    __tablename__ = "audit_logs"

    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction))
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="SUCCESS")
    detail: Mapped[dict] = mapped_column(JSON, default=dict)

    user: Mapped["User | None"] = relationship()  # noqa: F821
