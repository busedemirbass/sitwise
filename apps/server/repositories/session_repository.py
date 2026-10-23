"""
Session repository — çalışma oturumları veri erişim katmanı.
SW-029 / SW-030: docs/uml/class-server.md referans alınmıştır.
"""

from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Session

from models.session import WorkSession
from repositories.base import BaseRepository


class SessionRepository(BaseRepository[WorkSession]):
    """Çalışma oturumlarına erişim sağlayan repository sınıfı."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, WorkSession)

    def _parse_uuid(self, val: uuid.UUID | str) -> uuid.UUID:
        if isinstance(val, str):
            return uuid.UUID(val)
        return val

    def create_session(
        self, user_id: uuid.UUID | str, device: str = "webcam"
    ) -> WorkSession:
        """Yeni bir çalışma oturumu oluşturur ve kaydeder."""
        session = WorkSession(
            user_id=self._parse_uuid(user_id),
            device=device,
            started_at=datetime.now(timezone.utc),
        )
        return self.add(session)

    def get_by_id_and_user(
        self, session_id: uuid.UUID | str, user_id: uuid.UUID | str
    ) -> WorkSession | None:
        """Belirtilen kullanıcıya ait oturumu döner."""
        try:
            s_id = self._parse_uuid(session_id)
            u_id = self._parse_uuid(user_id)
        except (ValueError, AttributeError):
            return None

        return (
            self.db.query(WorkSession)
            .filter(WorkSession.id == s_id, WorkSession.user_id == u_id)
            .first()
        )

    def end_session(
        self, session_id: uuid.UUID | str, user_id: uuid.UUID | str
    ) -> WorkSession | None:
        """Oturumu sonlandırır ve ended_at zaman damgası ekler."""
        session = self.get_by_id_and_user(session_id, user_id)
        if session is None:
            return None

        if session.ended_at is None:
            session.ended_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(session)
        return session

    def list_by_user(
        self, user_id: uuid.UUID | str, limit: int = 50, offset: int = 0
    ) -> tuple[list[WorkSession], int]:
        """Kullanıcının geçmiş oturumlarını listeler ve toplam sayıyı döner."""
        try:
            u_id = self._parse_uuid(user_id)
        except (ValueError, AttributeError):
            return [], 0

        query = self.db.query(WorkSession).filter(WorkSession.user_id == u_id)
        total = query.count()
        sessions = (
            query.order_by(WorkSession.started_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return sessions, total
