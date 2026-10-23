"""
Session service — çalışma oturumları iş mantığı katmanı.
SW-029 / SW-030: docs/uml/class-server.md referans alınmıştır.
"""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status

from models.session import WorkSession
from repositories.session_repository import SessionRepository


class SessionService:
    """Çalışma oturumlarını yöneten servis sınıfı."""

    def __init__(self, session_repo: SessionRepository) -> None:
        self.session_repo = session_repo

    def start_session(
        self, user_id: uuid.UUID | str, device: str = "webcam"
    ) -> WorkSession:
        """Kullanıcı için yeni bir oturum başlatır."""
        return self.session_repo.create_session(user_id=user_id, device=device)

    def end_session(
        self, session_id: uuid.UUID | str, user_id: uuid.UUID | str
    ) -> WorkSession:
        """Açık oturumu kapatır. Bulunamazsa 404 fırlatır."""
        session = self.session_repo.end_session(session_id=session_id, user_id=user_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Oturum bulunamadı veya erişim yetkiniz yok.",
            )
        return session

    def get_session(
        self, session_id: uuid.UUID | str, user_id: uuid.UUID | str
    ) -> WorkSession:
        """Belirtilen oturumun ayrıntılarını döner."""
        session = self.session_repo.get_by_id_and_user(
            session_id=session_id, user_id=user_id
        )
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Oturum bulunamadı veya erişim yetkiniz yok.",
            )
        return session

    def list_sessions(
        self, user_id: uuid.UUID | str, limit: int = 50, offset: int = 0
    ) -> tuple[list[WorkSession], int]:
        """Kullanıcının geçmiş oturumlarını listeler."""
        return self.session_repo.list_by_user(
            user_id=user_id, limit=limit, offset=offset
        )
