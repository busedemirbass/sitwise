"""
DailySummary modeli — günlük ergonomi özeti.
SW-020: SQLAlchemy modelleri ve Alembic migration'ları

Alanlar API contract Bölüm 4.6.5'ten türetilmiştir:
  score        [0–100]
  good_minutes >= 0
  alert_count  >= 0
  avg_blink    [0.0–60.0]
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class DailySummary(Base):
    """Bir kullanıcının tek güne ait özet istatistikleri."""

    __tablename__ = "daily_summaries"

    __table_args__ = (
        # Her kullanıcı için günde en fazla bir özet
        UniqueConstraint("user_id", "date", name="uq_daily_summaries_user_date"),
        CheckConstraint(
            "score >= 0 AND score <= 100", name="ck_daily_summary_score_range"
        ),
        CheckConstraint("good_minutes >= 0", name="ck_daily_summary_good_minutes"),
        CheckConstraint("alert_count >= 0", name="ck_daily_summary_alert_count"),
        CheckConstraint(
            "avg_blink >= 0.0 AND avg_blink <= 60.0",
            name="ck_daily_summary_avg_blink_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Özet benzersiz tanımlayıcısı (UUID v4)",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Bu özete ait kullanıcı",
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Özet tarihi (YYYY-MM-DD)",
    )

    # Özet istatistikleri
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Günlük ergonomi skoru [0–100]",
    )
    good_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="İyi duruşta geçirilen toplam dakika",
    )
    alert_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Gün içinde tetiklenen uyarı sayısı",
    )
    avg_blink: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Gün boyunca ortalama göz kırpma/dakika [0.0–60.0]",
    )

    # Oluşturulma zamanı
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Özet oluşturulma zamanı (UTC)",
    )

    # İlişki
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="daily_summaries",
    )

    def __repr__(self) -> str:
        return (
            f"<DailySummary user_id={self.user_id!s} date={self.date} "
            f"score={self.score}>"
        )
