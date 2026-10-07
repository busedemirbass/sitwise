"""
User modeli — kullanıcı hesap bilgileri.
SW-020: SQLAlchemy modelleri ve Alembic migration'ları
docs/uml/er.md referans alınmıştır.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from models.calibration_profile import CalibrationProfile
    from models.daily_summary import DailySummary
    from models.fatigue_report import FatigueReport
    from models.session import WorkSession
    from models.threshold import UserThreshold


class User(Base):
    """Kullanıcı hesabını temsil eder."""

    __tablename__ = "users"

    # Birincil anahtar — UUID v4
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Kullanıcı benzersiz tanımlayıcısı (UUID v4)",
    )

    # Kimlik bilgileri
    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        comment="Kullanıcının görünen adı",
    )
    email: Mapped[str] = mapped_column(
        String(254),
        nullable=False,
        unique=True,
        index=True,
        comment="E-posta adresi (benzersiz, giriş anahtarı)",
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="bcrypt/argon2 ile hash'lenmiş şifre",
    )

    # Durum
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Hesap aktif mi?",
    )

    # Zaman damgaları
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Hesap oluşturulma zamanı (UTC)",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Son güncelleme zamanı (UTC)",
    )

    # İlişkiler
    sessions: Mapped[list[WorkSession]] = relationship(
        "WorkSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    calibration_profiles: Mapped[list[CalibrationProfile]] = relationship(
        "CalibrationProfile",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    thresholds: Mapped[list[UserThreshold]] = relationship(
        "UserThreshold",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    daily_summaries: Mapped[list[DailySummary]] = relationship(
        "DailySummary",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    fatigue_reports: Mapped[list[FatigueReport]] = relationship(
        "FatigueReport",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id!s} email={self.email!r}>"
