"""
Sessions router — çalışma oturumu başlatma, bitirme ve listeleme uçları.
SW-015: OpenAPI spesifikasyonu v1
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/sessions", tags=["Sessions"])


# ---------------------------------------------------------------------------
# Request / Response şemaları
# ---------------------------------------------------------------------------


class StartSessionRequest(BaseModel):
    """Oturum başlatma isteği."""

    device: str = "webcam"


class SessionResponse(BaseModel):
    """Tek bir oturum yanıtı."""

    id: str
    user_id: str
    started_at: datetime
    ended_at: datetime | None = None
    device: str


class SessionListResponse(BaseModel):
    """Oturum listesi yanıtı."""

    sessions: list[SessionResponse]
    total: int


# ---------------------------------------------------------------------------
# Uç noktalar
# ---------------------------------------------------------------------------


@router.post(
    "/",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni oturum başlat",
    description="Kullanıcı için yeni bir çalışma oturumu oluşturur ve döner.",
)
def start_session(body: StartSessionRequest) -> SessionResponse:
    """Yeni oturum açar; ilk metrik gönderiminden önce çağrılmalıdır."""
    # TODO (SW-impl): SessionService.start() çağrısı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")


@router.patch(
    "/{session_id}/end",
    response_model=SessionResponse,
    summary="Oturumu sonlandır",
    description="`ended_at` zaman damgasını ayarlar ve oturumu kapatır.",
)
def end_session(session_id: str) -> SessionResponse:
    """Açık oturumu kapatır."""
    # TODO (SW-impl): SessionService.end() çağrısı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")


@router.get(
    "/",
    response_model=SessionListResponse,
    summary="Oturum listesi",
    description="Giriş yapan kullanıcının tüm geçmiş oturumlarını döner.",
)
def list_sessions() -> SessionListResponse:
    """Kullanıcının oturum geçmişini döner."""
    # TODO (SW-impl): SessionService.list() çağrısı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Tek oturum detayı",
    description="Belirtilen oturumun ayrıntılarını döner.",
)
def get_session(session_id: str) -> SessionResponse:
    """Tek bir oturumun bilgilerini döner."""
    # TODO (SW-impl): SessionService.get() çağrısı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")
