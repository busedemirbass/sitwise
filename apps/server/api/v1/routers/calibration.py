"""
Calibration router — kullanıcı kalibrasyonu oluşturma ve sorgulama uçları.
SW-015: OpenAPI spesifikasyonu v1
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/calibration", tags=["Calibration"])


# ---------------------------------------------------------------------------
# Request / Response şemaları
# ---------------------------------------------------------------------------


class CalibrationCreateRequest(BaseModel):
    """Yeni kalibrasyon profili oluşturma isteği."""

    neck_mean: float = Field(..., description="Ortalama boyun eğim oranı")
    neck_std: float = Field(..., ge=0.0, description="Boyun standart sapması")
    shoulder_mean: float = Field(..., description="Ortalama omuz eğimi")
    shoulder_std: float = Field(..., ge=0.0, description="Omuz standart sapması")
    distance_cm: float = Field(..., ge=10.0, le=200.0, description="Ölçülen ekran mesafesi (cm)")


class CalibrationResponse(BaseModel):
    """Kalibrasyon profili yanıtı."""

    id: str
    user_id: str
    neck_mean: float
    neck_std: float
    shoulder_mean: float
    shoulder_std: float
    distance_cm: float
    created_at: datetime


# ---------------------------------------------------------------------------
# Uç noktalar
# ---------------------------------------------------------------------------


@router.post(
    "/",
    response_model=CalibrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Kalibrasyon profili oluştur",
    description="Kullanıcının oturma düzenine göre yeni bir referans profil oluşturur.",
)
def create_calibration(body: CalibrationCreateRequest) -> CalibrationResponse:
    """Yeni kalibrasyon profili kaydeder."""
    # TODO (SW-impl): CalibrationService.create() çağrısı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")


@router.get(
    "/latest",
    response_model=CalibrationResponse,
    summary="Son kalibrasyon profili",
    description="Kullanıcının en son oluşturduğu kalibrasyon profilini döner.",
)
def latest_calibration() -> CalibrationResponse:
    """Aktif (en son) kalibrasyon profilini döner."""
    # TODO (SW-impl): CalibrationRepository.latest() çağrısı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")


@router.get(
    "/{profile_id}",
    response_model=CalibrationResponse,
    summary="Kalibrasyon profili detayı",
    description="Belirtilen ID'ye sahip kalibrasyon profilini döner.",
)
def get_calibration(profile_id: str) -> CalibrationResponse:
    """Tek bir kalibrasyon profilini döner."""
    # TODO (SW-impl): CalibrationRepository.get() çağrısı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")
