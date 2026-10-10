"""
User repository — kullanıcı veri tabanı erişim katmanı.
SW-014 ve SW-021: docs/uml/class-server.md referans alınmıştır.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from models.user import User
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Kullanıcı verilerine erişim sağlayan repository."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, User)

    def get_by_email(self, email: str) -> User | None:
        """E-posta adresine göre kullanıcı arar."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: uuid.UUID | str) -> User | None:
        """UUID veya dize formatındaki kimliğe göre kullanıcı arar."""
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                return None
        return self.get(user_id)
