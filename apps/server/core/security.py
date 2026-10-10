"""
Güvenlik yardımcıları — şifre hashleme ve JWT işlemleri (SW-021).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any

import bcrypt
import jwt

SECRET_KEY: str = os.environ.get(
    "JWT_SECRET_KEY", "sitwise-dev-super-secret-key-change-in-production"
)
ALGORITHM: str = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
)


def hash_password(password: str) -> str:
    """Düz metin şifreyi bcrypt ile hashler."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Düz metin şifrenin hash ile eşleştiğini doğrular."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Verilen payload için imzalı bir JWT erişim jetonu üretir."""
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """JWT erişim jetonunu doğrular ve payload sözlüğünü döner."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
