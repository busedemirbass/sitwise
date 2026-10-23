"""
Sessions router — çalışma oturumu başlatma, bitirme ve listeleme uçları.
SW-015 / SW-029: OpenAPI spesifikasyonu v1 ve uç nokta uygulaması.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.deps import get_current_user
from db.session import get_db
from models.user import User
from repositories.session_repository import SessionRepository
from services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["Sessions"])


# ---------------------------------------------------------------------------
# Request / Response şemaları
# ---------------------------------------------------------------------------


class StartSessionRequest(BaseModel):
    """Oturum başlatma isteği."""

    device: str = Field(default="webcam", min_length=1, max_length=100)


class SessionResponse(BaseModel):
    """Tek bir oturum yanıtı."""

    id: str
    user_id: str
    started_at: datetime
    ended_at: datetime | None = None
    device: str

    class Config:
        from_attributes = True


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
def start_session(
    body: StartSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SessionResponse:
    """Yeni oturum açar; ilk metrik gönderiminden önce çağrılmalıdır."""
    service = SessionService(SessionRepository(db))
    session = service.start_session(user_id=current_user.id, device=body.device)
    return SessionResponse(
        id=str(session.id),
        user_id=str(session.user_id),
        started_at=session.started_at,
        ended_at=session.ended_at,
        device=session.device,
    )


@router.patch(
    "/{session_id}/end",
    response_model=SessionResponse,
    summary="Oturumu sonlandır",
    description="`ended_at` zaman damgasını ayarlar ve oturumu kapatır.",
)
def end_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SessionResponse:
    """Açık oturumu kapatır."""
    service = SessionService(SessionRepository(db))
    session = service.end_session(session_id=session_id, user_id=current_user.id)
    return SessionResponse(
        id=str(session.id),
        user_id=str(session.user_id),
        started_at=session.started_at,
        ended_at=session.ended_at,
        device=session.device,
    )


@router.get(
    "/",
    response_model=SessionListResponse,
    summary="Oturum listesi",
    description="Giriş yapan kullanıcının tüm geçmiş oturumlarını döner.",
)
def list_sessions(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SessionListResponse:
    """Kullanıcının oturum geçmişini döner."""
    service = SessionService(SessionRepository(db))
    sessions, total = service.list_sessions(
        user_id=current_user.id, limit=limit, offset=offset
    )
    return SessionListResponse(
        sessions=[
            SessionResponse(
                id=str(s.id),
                user_id=str(s.user_id),
                started_at=s.started_at,
                ended_at=s.ended_at,
                device=s.device,
            )
            for s in sessions
        ],
        total=total,
    )


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Tek oturum detayı",
    description="Belirtilen oturumun ayrıntılarını döner.",
)
def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SessionResponse:
    """Tek bir oturumun bilgilerini döner."""
    service = SessionService(SessionRepository(db))
    session = service.get_session(session_id=session_id, user_id=current_user.id)
    return SessionResponse(
        id=str(session.id),
        user_id=str(session.user_id),
        started_at=session.started_at,
        ended_at=session.ended_at,
        device=session.device,
    )
