"""
Auth service — kimlik doğrulama, kullanıcı kaydı ve jeton yönetimi iş mantığı.
SW-014 ve SW-021: docs/uml/class-server.md referans alınmıştır.
"""

from __future__ import annotations

from fastapi import HTTPException, status
import jwt

from core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from models.user import User
from repositories.user_repository import UserRepository


class AuthService:
    """Kimlik doğrulama ve kullanıcı oturumu servis katmanı."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def register(self, name: str, email: str, password: str) -> str:
        """Yeni kullanıcı kaydeder ve JWT erişim jetonu üretir."""
        normalized_email = email.strip().lower()

        existing_user = self.user_repo.get_by_email(normalized_email)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu e-posta adresi zaten kullanımda.",
            )

        password_hash = hash_password(password)
        new_user = User(
            name=name.strip(),
            email=normalized_email,
            password_hash=password_hash,
            is_active=True,
        )
        saved_user = self.user_repo.add(new_user)

        token_data = {
            "sub": str(saved_user.id),
            "email": saved_user.email,
        }
        return create_access_token(token_data)

    def login(self, email: str, password: str) -> str:
        """Kullanıcı kimliğini doğrular ve JWT erişim jetonu döner."""
        normalized_email = email.strip().lower()

        user = self.user_repo.get_by_email(normalized_email)
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz e-posta veya şifre.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kullanıcı hesabı devre dışı bırakılmış.",
            )

        token_data = {
            "sub": str(user.id),
            "email": user.email,
        }
        return create_access_token(token_data)

    def verify_token(self, token: str) -> User:
        """JWT jetonunu doğrular ve ilişkili kullanıcıyı döner."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz veya süresi dolmuş oturum jetonu.",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = decode_access_token(token)
            user_id: str | None = payload.get("sub")
            if not user_id:
                raise credentials_exception
        except (jwt.PyJWTError, ValueError):
            raise credentials_exception

        user = self.user_repo.get_by_id(user_id)
        if user is None or not user.is_active:
            raise credentials_exception

        return user
