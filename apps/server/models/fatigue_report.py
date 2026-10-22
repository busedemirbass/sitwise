"""
FatigueReport modeli — kullanıcı yorgunluk bildirimleri / anket skorları.
SW-020: SQLAlchemy modelleri ve Alembic migration'ları
docs/uml/er.md referans alınmıştır.
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class FatigueReport(Base):
    """Kullanıcının öznel yorgunluk skorunu temsil eder."""

    __tablename__ = "fatigue_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Rapor benzersiz tanımlayıcısı (UUID v4)",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Bu raporun ait olduğu kullanıcı",
    )
    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Rapor tarihi (YYYY-MM-DD)",
    )
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Yorgunluk puanı [1-10 veya 0-100]",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Oluşturulma zamanı (UTC)",
    )

    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="fatigue_reports",
    )

    def __repr__(self) -> str:
        return (
            f"<FatigueReport user_id={self.user_id!s} date={self.date} "
            f"score={self.score}>"
        )
