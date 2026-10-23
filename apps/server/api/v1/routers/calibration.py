"""
Calibration router — kullanıcı kalibrasyonu oluşturma ve sorgulama uçları.
SW-015 / SW-029: OpenAPI spesifikasyonu v1 ve uç nokta uygulaması.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.deps import get_current_user
from db.session import get_db
from models.user import User
from repositories.calibration_repository import CalibrationRepository
from services.calibration_service import CalibrationService

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
    distance_cm: float = Field(
        ..., ge=10.0, le=200.0, description="Ölçülen ekran mesafesi (cm)"
    )


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

    class Config:
        from_attributes = True


class CalibrationListResponse(BaseModel):
    """Kalibrasyon profilleri listesi yanıtı."""

    profiles: list[CalibrationResponse]
    total: int


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
def create_calibration(
    body: CalibrationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CalibrationResponse:
    """Yeni kalibrasyon profili kaydeder."""
    service = CalibrationService(CalibrationRepository(db))
    profile = service.create_calibration(
        user_id=current_user.id,
        neck_mean=body.neck_mean,
        neck_std=body.neck_std,
        shoulder_mean=body.shoulder_mean,
        shoulder_std=body.shoulder_std,
        distance_cm=body.distance_cm,
    )
    return CalibrationResponse(
        id=str(profile.id),
        user_id=str(profile.user_id),
        neck_mean=profile.neck_mean,
        neck_std=profile.neck_std,
        shoulder_mean=profile.shoulder_mean,
        shoulder_std=profile.shoulder_std,
        distance_cm=profile.distance_cm,
        created_at=profile.created_at,
    )


@router.get(
    "/latest",
    response_model=CalibrationResponse,
    summary="Son kalibrasyon profili",
    description="Kullanıcının en son oluşturduğu kalibrasyon profilini döner.",
)
def latest_calibration(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CalibrationResponse:
    """Aktif (en son) kalibrasyon profilini döner."""
    service = CalibrationService(CalibrationRepository(db))
    profile = service.get_latest(user_id=current_user.id)
    return CalibrationResponse(
        id=str(profile.id),
        user_id=str(profile.user_id),
        neck_mean=profile.neck_mean,
        neck_std=profile.neck_std,
        shoulder_mean=profile.shoulder_mean,
        shoulder_std=profile.shoulder_std,
        distance_cm=profile.distance_cm,
        created_at=profile.created_at,
    )


@router.get(
    "/",
    response_model=CalibrationListResponse,
    summary="Kalibrasyon geçmişi listele",
    description="Kullanıcının tüm geçmiş kalibrasyon profillerini döner.",
)
def list_calibrations(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CalibrationListResponse:
    """Kullanıcının tüm kalibrasyon profillerini döner."""
    service = CalibrationService(CalibrationRepository(db))
    profiles = service.list_calibrations(
        user_id=current_user.id, limit=limit, offset=offset
    )
    return CalibrationListResponse(
        profiles=[
            CalibrationResponse(
                id=str(p.id),
                user_id=str(p.user_id),
                neck_mean=p.neck_mean,
                neck_std=p.neck_std,
                shoulder_mean=p.shoulder_mean,
                shoulder_std=p.shoulder_std,
                distance_cm=p.distance_cm,
                created_at=p.created_at,
            )
            for p in profiles
        ],
        total=len(profiles),
    )


@router.get(
    "/{profile_id}",
    response_model=CalibrationResponse,
    summary="Kalibrasyon profili detayı",
    description="Belirtilen ID'ye sahip kalibrasyon profilini döner.",
)
def get_calibration(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CalibrationResponse:
    """Tek bir kalibrasyon profilini döner."""
    repo = CalibrationRepository(db)
    profile = repo.get(profile_id)
    if profile is None or str(profile.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kalibrasyon profili bulunamadı veya erişim yetkiniz yok.",
        )
    return CalibrationResponse(
        id=str(profile.id),
        user_id=str(profile.user_id),
        neck_mean=profile.neck_mean,
        neck_std=profile.neck_std,
        shoulder_mean=profile.shoulder_mean,
        shoulder_std=profile.shoulder_std,
        distance_cm=profile.distance_cm,
        created_at=profile.created_at,
    )
