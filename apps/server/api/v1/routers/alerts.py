"""
Alerts router — ergonomi uyarılarını listeleme ve geri bildirim uçları.
SW-015: OpenAPI spesifikasyonu v1
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

router = APIRouter(prefix="/alerts", tags=["Alerts"])


# ---------------------------------------------------------------------------
# Request / Response şemaları
# ---------------------------------------------------------------------------


class AlertResponse(BaseModel):
    """Tek bir uyarı yanıtı."""

    id: str
    session_id: str
    ts: datetime
    type: str = "posture"  # "posture" | "eye_fatigue" | "distance"
    severity: str = "medium"  # "low" | "medium" | "high"


class AlertListResponse(BaseModel):
    """Uyarı listesi yanıtı."""

    alerts: list[AlertResponse]
    total: int


class AlertFeedbackRequest(BaseModel):
    """Kullanıcı uyarı geri bildirimi."""

    is_false: bool


class AlertFeedbackResponse(BaseModel):
    """Geri bildirim kayıt yanıtı."""

    alert_id: str
    is_false: bool
    created_at: datetime


# ---------------------------------------------------------------------------
# Uç noktalar
# ---------------------------------------------------------------------------


@router.get(
    "/",
    response_model=AlertListResponse,
    summary="Uyarı listesi",
    description=(
        "Giriş yapan kullanıcının uyarılarını döner; isteğe bağlı oturum filtresi."
    ),
)
def list_alerts(
    session_id: str | None = Query(None, description="Filtre: oturum ID'si"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> AlertListResponse:
    """Kullanıcıya ait ergonomi uyarılarını listeler."""
    # TODO (SW-impl): AlertRepository.get_user_alerts() çağrısı eklenecek
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı"
    )


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
    summary="Tek uyarı detayı",
    description="Belirtilen uyarının ayrıntılarını döner.",
)
def get_alert(alert_id: str) -> AlertResponse:
    """Tek bir uyarının bilgilerini döner."""
    # TODO (SW-impl): AlertRepository.get() çağrısı eklenecek
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı"
    )


@router.post(
    "/{alert_id}/feedback",
    response_model=AlertFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Uyarıya geri bildirim ver",
    description="Kullanıcı uyarının yanlış pozitif olup olmadığını bildirir.",
)
def submit_feedback(alert_id: str, body: AlertFeedbackRequest) -> AlertFeedbackResponse:
    """Uyarı için is_false geri bildirimini kaydeder."""
    # TODO (SW-impl): AlertRepository.save_feedback() çağrısı eklenecek
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı"
    )
