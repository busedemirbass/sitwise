"""
Auth router — kullanıcı kaydı, girişi, çıkışı ve profil uçları.
SW-015: OpenAPI spesifikasyonu v1
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

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
def register(body: RegisterRequest) -> TokenResponse:
    """Yeni kullanıcı oluşturur ve erişim jetonu döner."""
    # TODO (SW-impl): AuthService.register() çağrısı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Kullanıcı girişi",
    description="Kimlik doğrulaması yapar ve JWT döner.",
)
def login(body: LoginRequest) -> TokenResponse:
    """Kullanıcıyı doğrular ve erişim jetonu döner."""
    # TODO (SW-impl): AuthService.login() çağrısı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Kullanıcı çıkışı",
    description="Geçerli jetonu geçersiz kılar (token blacklist).",
)
def logout() -> None:
    """Aktif oturumu sonlandırır."""
    # TODO (SW-impl): Token kara listesi eklenecek
    return None


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Mevcut kullanıcı profili",
    description="JWT'den kimliği çözümlenen kullanıcının profil bilgilerini döner.",
)
def me() -> UserResponse:
    """Giriş yapmış kullanıcının profilini döner."""
    # TODO (SW-impl): JWT bağımlılığı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")
