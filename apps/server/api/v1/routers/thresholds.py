"""
Thresholds router — kullanıcı kişisel eşik değerleri yönetim uçları.
SW-015: OpenAPI spesifikasyonu v1
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/thresholds", tags=["Thresholds"])


# ---------------------------------------------------------------------------
# Request / Response şemaları
# ---------------------------------------------------------------------------


class ThresholdResponse(BaseModel):
    """Tek eşik değeri yanıtı."""

    id: str
    user_id: str
    metric: str
    value: float
    updated_at: datetime


class ThresholdListResponse(BaseModel):
    """Eşik değerleri listesi yanıtı."""

    thresholds: list[ThresholdResponse]


class ThresholdUpsertRequest(BaseModel):
    """Eşik değeri oluşturma / güncelleme isteği."""

    metric: str = Field(
        ...,
        description="Metrik adı: 'neck_ratio' | 'shoulder_tilt' | 'distance_cm' | 'blinks_per_min'",
    )
    value: float = Field(..., description="Yeni eşik değeri")


# ---------------------------------------------------------------------------
# Uç noktalar
# ---------------------------------------------------------------------------


@router.get(
    "/",
    response_model=ThresholdListResponse,
    summary="Eşik değerleri listesi",
    description="Kullanıcının tüm kişisel eşik değerlerini döner.",
)
def list_thresholds() -> ThresholdListResponse:
    """Tüm kullanıcı eşiklerini döner."""
    # TODO (SW-impl): ThresholdRepository.list() çağrısı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")


@router.put(
    "/",
    response_model=ThresholdResponse,
    summary="Eşik değeri oluştur veya güncelle",
    description="Belirtilen metrik için eşik değerini ayarlar (upsert).",
)
def upsert_threshold(body: ThresholdUpsertRequest) -> ThresholdResponse:
    """Metrik eşiğini oluşturur ya da mevcut değeri günceller."""
    # TODO (SW-impl): ThresholdRepository.upsert() çağrısı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")


@router.delete(
    "/{metric}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eşik değeri sil",
    description="Belirtilen metriğin eşik değerini kaldırır; sistem varsayılanına döner.",
)
def delete_threshold(metric: str) -> None:
    """Kullanıcıya özel eşik değerini siler."""
    # TODO (SW-impl): ThresholdRepository.delete() çağrısı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")
