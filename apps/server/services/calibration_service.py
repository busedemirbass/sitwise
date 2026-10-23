"""
Calibration service — kalibrasyon profilleri iş mantığı katmanı.
SW-029 / SW-030: docs/uml/class-server.md referans alınmıştır.
"""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status

from models.calibration_profile import CalibrationProfile
from repositories.calibration_repository import CalibrationRepository


class CalibrationService:
    """Kalibrasyon profillerini yöneten servis sınıfı."""

    def __init__(self, calibration_repo: CalibrationRepository) -> None:
        self.calibration_repo = calibration_repo

    def create_calibration(
        self,
        user_id: uuid.UUID | str,
        neck_mean: float,
        neck_std: float,
        shoulder_mean: float,
        shoulder_std: float,
        distance_cm: float,
    ) -> CalibrationProfile:
        """Yeni bir kalibrasyon profili kaydeder."""
        return self.calibration_repo.create_profile(
            user_id=user_id,
            neck_mean=neck_mean,
            neck_std=neck_std,
            shoulder_mean=shoulder_mean,
            shoulder_std=shoulder_std,
            distance_cm=distance_cm,
        )

    def get_latest(self, user_id: uuid.UUID | str) -> CalibrationProfile:
        """Kullanıcının en güncel kalibrasyon profilini döner.
        Bulunamazsa 404 fırlatır.
        """
        profile = self.calibration_repo.get_latest_by_user(user_id=user_id)
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Henüz kalibrasyon profili oluşturulmamış.",
            )
        return profile

    def list_calibrations(
        self, user_id: uuid.UUID | str, limit: int = 50, offset: int = 0
    ) -> list[CalibrationProfile]:
        """Kullanıcının tüm geçmiş kalibrasyon profillerini listeler."""
        return self.calibration_repo.list_by_user(
            user_id=user_id, limit=limit, offset=offset
        )
