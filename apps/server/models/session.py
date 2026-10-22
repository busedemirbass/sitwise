"""
WorkSession modeli — kullanıcının çalışma oturumu.
SW-020: SQLAlchemy modelleri ve Alembic migration'ları
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class WorkSession(Base):
    """Tek bir çalışma oturumunu temsil eder."""

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Oturum benzersiz tanımlayıcısı (UUID v4)",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Bu oturumun sahibi olan kullanıcı",
    )

    # Oturum zamanları
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Oturum başlangıç zamanı (UTC)",
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Oturum bitiş zamanı (UTC); NULL ise oturum açık",
    )

    # Cihaz bilgisi (varsayılan: webcam)
    device: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="webcam",
        comment="Kullanılan kamera/cihaz adı",
    )

    # İlişkiler
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="sessions",
    )
    metric_samples: Mapped[list["MetricSample"]] = relationship(  # noqa: F821
        "MetricSample",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    alerts: Mapped[list["Alert"]] = relationship(  # noqa: F821
        "Alert",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<WorkSession id={self.id!s} user_id={self.user_id!s}>"
