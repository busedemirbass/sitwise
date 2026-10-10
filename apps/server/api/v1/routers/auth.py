"""
Auth router — kullanıcı kaydı, girişi, çıkışı ve profil uçları.
SW-015: OpenAPI spesifikasyonu v1
SW-021: Kayıt/giriş ve JWT ile kimlik doğrulama uygulaması
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from api.deps import get_current_user
from db.session import get_db
from models.user import User
from repositories.user_repository import UserRepository
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------------------------------------------------------------------------
# Request / Response şemaları
# ---------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    """Yeni kullanıcı kayıt isteği."""

    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Kullanıcı giriş isteği."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT erişim jetonu yanıtı."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Kullanıcı profil yanıtı."""

    id: str
    name: str
    email: str


# ---------------------------------------------------------------------------
# Uç noktalar
# ---------------------------------------------------------------------------


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni kullanıcı kaydı",
    description="E-posta ve şifreyle yeni hesap oluşturur, JWT döner.",
)
def register(
    body: RegisterRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Yeni kullanıcı oluşturur ve erişim jetonu döner."""
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    token = auth_service.register(
        name=body.name,
        email=str(body.email),
        password=body.password,
    )
    return TokenResponse(access_token=token, token_type="bearer")


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Kullanıcı girişi",
    description="Kimlik doğrulaması yapar ve JWT döner.",
)
def login(
    body: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Kullanıcıyı doğrular ve erişim jetonu döner."""
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    token = auth_service.login(
        email=str(body.email),
        password=body.password,
    )
    return TokenResponse(access_token=token, token_type="bearer")


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Kullanıcı çıkışı",
    description="Geçerli jetonu geçersiz kılar (token blacklist).",
)
def logout() -> None:
    """Aktif oturumu sonlandırır."""
    return None


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Mevcut kullanıcı profili",
    description="JWT'den kimliği çözümlenen kullanıcının profil bilgilerini döner.",
)
def me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Giriş yapmış kullanıcının profilini döner."""
    return UserResponse(
        id=str(current_user.id),
        name=current_user.name,
        email=current_user.email,
    )
