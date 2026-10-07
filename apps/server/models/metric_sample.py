"""
MetricSample modeli — tek bir ergonomi ölçüm örneği.
SW-020: SQLAlchemy modelleri ve Alembic migration'ları
docs/uml/er.md ve docs/api/contract.md referans alınmıştır.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class MetricSample(Base):
    """Tek bir zaman noktasına ait ergonomi metrik örneklemesi."""

    __tablename__ = "metric_samples"

    __table_args__ = (
        CheckConstraint(
            "neck_ratio >= 0.0 AND neck_ratio <= 2.0", name="ck_neck_ratio_range"
        ),
        CheckConstraint(
            "shoulder_tilt >= -90.0 AND shoulder_tilt <= 90.0",
            name="ck_shoulder_tilt_range",
        ),
        CheckConstraint(
            "distance_cm >= 10.0 AND distance_cm <= 200.0",
            name="ck_distance_cm_range",
        ),
        CheckConstraint(
            "blinks_per_min >= 0 AND blinks_per_min <= 60",
            name="ck_blinks_per_min_range",
        ),
        # Zaman serisi sorguları için bileşik index
        Index("ix_metric_samples_session_ts", "session_id", "ts"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
        comment="Örnek benzersiz tanımlayıcısı (BigInt autoincrement)",
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        comment="Bu örneğin ait olduğu oturum",
    )

    # Zaman damgası — UTC ISO 8601
    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Örnek alınma zamanı (UTC)",
    )

    # Ergonomi metrikleri
    neck_ratio: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Boyun oranı [0.0–2.0]; 1.0 dik duruş",
    )
    shoulder_tilt: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Omuz eğimi [-90°–+90°]; 0 dik",
    )
    distance_cm: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Ekrana mesafe [10–200 cm]",
    )
    blinks_per_min: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Dakikada göz kırpma sayısı [0–60]",
    )
    state: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Genel durum: good / warning / bad",
    )

    # İlişki
    session: Mapped["WorkSession"] = relationship(  # noqa: F821
        "WorkSession",
        back_populates="metric_samples",
    )

    def __repr__(self) -> str:
        return (
            f"<MetricSample id={self.id} session_id={self.session_id!s} "
            f"state={self.state!r}>"
        )
