"""
Calibration repository — kalibrasyon profilleri veri erişim katmanı.
SW-029 / SW-030: docs/uml/class-server.md referans alınmıştır.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from models.calibration_profile import CalibrationProfile
from repositories.base import BaseRepository


class CalibrationRepository(BaseRepository[CalibrationProfile]):
    """Kalibrasyon profillerine erişim sağlayan repository sınıfı."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, CalibrationProfile)

    def _parse_uuid(self, val: uuid.UUID | str) -> uuid.UUID:
        if isinstance(val, str):
            return uuid.UUID(val)
        return val

    def create_profile(
        self,
        user_id: uuid.UUID | str,
        neck_mean: float,
        neck_std: float,
        shoulder_mean: float,
        shoulder_std: float,
        distance_cm: float,
    ) -> CalibrationProfile:
        """Kullanıcı için yeni kalibrasyon profili kaydeder."""
        profile = CalibrationProfile(
            user_id=self._parse_uuid(user_id),
            neck_mean=neck_mean,
            neck_std=neck_std,
            shoulder_mean=shoulder_mean,
            shoulder_std=shoulder_std,
            distance_cm=distance_cm,
        )
        return self.add(profile)

    def get_latest_by_user(
        self, user_id: uuid.UUID | str
    ) -> CalibrationProfile | None:
        """Kullanıcının en son oluşturulmuş kalibrasyon profilini döner."""
        try:
            u_id = self._parse_uuid(user_id)
        except (ValueError, AttributeError):
            return None

        return (
            self.db.query(CalibrationProfile)
            .filter(CalibrationProfile.user_id == u_id)
            .order_by(CalibrationProfile.created_at.desc())
            .first()
        )

    def list_by_user(
        self, user_id: uuid.UUID | str, limit: int = 50, offset: int = 0
    ) -> list[CalibrationProfile]:
        """Kullanıcının tüm geçmiş kalibrasyon profillerini listeler."""
        try:
            u_id = self._parse_uuid(user_id)
        except (ValueError, AttributeError):
            return []

        return (
            self.db.query(CalibrationProfile)
            .filter(CalibrationProfile.user_id == u_id)
            .order_by(CalibrationProfile.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
