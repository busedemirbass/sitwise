"""
UserThreshold modeli — kullanıcıya özgü metrik eşik değerleri.
SW-020: SQLAlchemy modelleri ve Alembic migration'ları
docs/uml/er.md ve docs/api/contract.md referans alınmıştır.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class UserThreshold(Base):
    """Kullanıcının bir metrik için özelleştirdiği eşik değeri."""

    __tablename__ = "user_thresholds"

    __table_args__ = (
        UniqueConstraint("user_id", "metric", name="uq_user_thresholds_user_metric"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Eşik değeri benzersiz tanımlayıcısı (UUID v4)",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Bu eşik değerinin sahibi kullanıcı",
    )

    metric: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Eşiğin uygulandığı metrik adı",
    )
    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Uyarı tetikleme eşik değeri",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Eşik değeri son güncelleme zamanı (UTC)",
    )

    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="thresholds",
    )

    def __repr__(self) -> str:
        return (
            f"<UserThreshold user_id={self.user_id!s} "
            f"metric={self.metric!r} value={self.value}>"
        )
