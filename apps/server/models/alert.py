"""
Alert ve AlertFeedback modelleri — kullanıcı uyarıları ve geri bildirim.
SW-020: SQLAlchemy modelleri ve Alembic migration'ları
docs/uml/er.md ve docs/api/contract.md referans alınmıştır.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Alert(Base):
    """Tek bir ergonomi uyarısını temsil eder."""

    __tablename__ = "alerts"

    __table_args__ = (Index("ix_alerts_session_ts", "session_id", "ts"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Uyarı benzersiz tanımlayıcısı (UUID v4)",
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Bu uyarının ait olduğu oturum",
    )

    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Uyarının oluşturulma zamanı (UTC)",
    )
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Uyarı türü: posture / eye_fatigue / distance",
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Uyarı şiddeti: low / medium / high",
    )

    # İlişkiler
    session: Mapped["WorkSession"] = relationship(  # noqa: F821
        "WorkSession",
        back_populates="alerts",
    )
    feedback: Mapped["AlertFeedback | None"] = relationship(
        "AlertFeedback",
        back_populates="alert",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Alert id={self.id!s} type={self.type!r} severity={self.severity!r}>"


class AlertFeedback(Base):
    """Kullanıcının 'yanlış pozitif' geri bildirimi."""

    __tablename__ = "alert_feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Geri bildirim benzersiz tanımlayıcısı (UUID v4)",
    )
    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("alerts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="Geri bildirimin yapıldığı uyarı",
    )

    is_false: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        comment="True ise kullanıcı bu uyarıyı yanlış pozitif olarak bildirdi",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Geri bildirim oluşturulma zamanı (UTC)",
    )

    # İlişki
    alert: Mapped["Alert"] = relationship(
        "Alert",
        back_populates="feedback",
    )

    def __repr__(self) -> str:
        return (
            f"<AlertFeedback id={self.id!s} alert_id={self.alert_id!s} "
            f"is_false={self.is_false}>"
        )
