"""
FastAPI ortak bağımlılıkları — veritabanı ve kimlik doğrulama.
SW-021: Korumalı uç noktalar için get_current_user bağımlılığı.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User
from repositories.user_repository import UserRepository
from services.auth_service import AuthService

# Bearer şeması (auto_error=False ile eksik token durumunu özel mesajla 401 yapıyoruz)
security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Aktif JWT token'ını doğrular ve mevcut kullanıcıyı döner."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kimlik doğrulama başlığı eksik.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    return auth_service.verify_token(credentials.credentials)
