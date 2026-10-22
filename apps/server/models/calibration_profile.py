"""
CalibrationProfile modeli — kullanıcıya özgü kalibrasyon profili.
SW-020: SQLAlchemy modelleri ve Alembic migration'ları

Alanlar API contract Bölüm 4.6.6'dan türetilmiştir:
  neck_mean, neck_std, shoulder_mean, shoulder_std, distance_cm
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class CalibrationProfile(Base):
    """Kullanıcının kamerasına ve fiziksel konumuna özgü kalibrasyon verisi."""

    __tablename__ = "calibration_profiles"

    __table_args__ = (
        CheckConstraint("neck_std >= 0.0", name="ck_calib_neck_std_positive"),
        CheckConstraint("shoulder_std >= 0.0", name="ck_calib_shoulder_std_positive"),
        CheckConstraint(
            "distance_cm >= 10.0 AND distance_cm <= 200.0",
            name="ck_calib_distance_cm_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Kalibrasyon profili benzersiz tanımlayıcısı (UUID v4)",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Bu profile ait kullanıcı",
    )

    # Boyun istatistikleri — kalibrasyondan hesaplanan ortalama ve std sapma
    neck_mean: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Kalibrasyondan hesaplanan boyun oranı ortalaması",
    )
    neck_std: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Kalibrasyondan hesaplanan boyun oranı standart sapması",
    )

    # Omuz istatistikleri
    shoulder_mean: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Kalibrasyondan hesaplanan omuz eğimi ortalaması",
    )
    shoulder_std: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Kalibrasyondan hesaplanan omuz eğimi standart sapması",
    )

    # Referans ekran mesafesi
    distance_cm: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Kalibrasyon sırasındaki ekrana olan referans mesafe (cm)",
    )

    # Oluşturulma zamanı — en son profile göre sıralamada kullanılır
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Kalibrasyon profili oluşturulma zamanı (UTC)",
    )

    # İlişki
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="calibration_profiles",
    )

    def __repr__(self) -> str:
        return (
            f"<CalibrationProfile id={self.id!s} user_id={self.user_id!s} "
            f"created_at={self.created_at.isoformat()!r}>"
        )
