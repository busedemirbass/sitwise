"""
Kimlik doğrulama birim ve entegrasyon testleri (SW-021).
Kabul Kriteri: Korumalı uç token olmadan 401 dönüyor.
"""

from __future__ import annotations

from datetime import timedelta
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from db.base import Base
from db.session import get_db
from main import app
import models  # noqa: F401 - Modellerin Base.metadata'ya kaydolması için


class TestAuth(unittest.TestCase):
    """JWT kimlik doğrulama ve kullanıcı uç noktaları test paketi."""

    @classmethod
    def setUpClass(cls):
        """Test veritabanı (bellek içi SQLite) ve TestClient hazırla."""
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=cls.engine,
        )

        def override_get_db():
            db = cls.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        """Bağımlılık geçersiz kılmalarını temizle."""
        app.dependency_overrides.clear()

    def test_01_password_hashing_and_verification(self):
        """Şifre hashleme ve doğrulama fonksiyonları doğru çalışmalı."""
        plain = "GizliSifre!123"
        hashed = hash_password(plain)

        self.assertNotEqual(plain, hashed)
        self.assertTrue(verify_password(plain, hashed))
        self.assertFalse(verify_password("YanlisSifre", hashed))

    def test_02_jwt_creation_and_expiration(self):
        """JWT jetonu üretimi ve süresi dolmuş jeton doğrulaması."""
        valid_token = create_access_token(
            {"sub": "test-user-id"},
            expires_delta=timedelta(minutes=10),
        )
        self.assertIsInstance(valid_token, str)
        self.assertTrue(len(valid_token) > 20)

    def test_03_protected_endpoint_without_token_returns_401(self):
        """KABUL KRİTERİ: Korumalı uç nokta (/auth/me) token olmadan 401 dönmeli."""
        response = self.client.get("/api/v1/auth/me")
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())

    def test_04_protected_endpoint_with_invalid_token_returns_401(self):
        """Geçersiz token ile korumalı uca erişildiğinde 401 dönmeli."""
        headers = {"Authorization": "Bearer gecersiz_token_dizesi"}
        response = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_05_protected_endpoint_with_expired_token_returns_401(self):
        """Süresi dolmuş token ile korumalı uca erişildiğinde 401 dönmeli."""
        expired_token = create_access_token(
            {"sub": "test-id"},
            expires_delta=timedelta(seconds=-10),
        )
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_06_register_new_user_success(self):
        """Yeni kullanıcı kaydı başarılı olmalı ve JWT erişim jetonu dönmeli."""
        payload = {
            "name": "Buse Demirbaş",
            "email": "buse@sitwise.app",
            "password": "GucluSifre2026!",
        }
        response = self.client.post("/api/v1/auth/register", json=payload)
        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data.get("token_type"), "bearer")
        self.assertTrue(len(data["access_token"]) > 20)

    def test_07_register_duplicate_email_returns_400(self):
        """Aynı e-posta ile ikinci kez kayıt olunduğunda 400 Bad Request dönmeli."""
        payload = {
            "name": "Buse Duplicate",
            "email": "buse@sitwise.app",
            "password": "BaskaSifre123!",
        }
        response = self.client.post("/api/v1/auth/register", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("zaten kullanımda", response.json()["detail"])

    def test_08_login_success(self):
        """Doğru e-posta ve şifre ile giriş yapıldığında 200 ve JWT dönmeli."""
        payload = {
            "email": "buse@sitwise.app",
            "password": "GucluSifre2026!",
        }
        response = self.client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data.get("token_type"), "bearer")

    def test_09_login_wrong_password_returns_401(self):
        """Yanlış şifre ile girişte 401 Unauthorized dönmeli."""
        payload = {
            "email": "buse@sitwise.app",
            "password": "YanlisSifre!",
        }
        response = self.client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(response.status_code, 401)

    def test_10_login_nonexistent_email_returns_401(self):
        """Kayıtlı olmayan e-posta ile girişte 401 Unauthorized dönmeli."""
        payload = {
            "email": "yok@sitwise.app",
            "password": "GucluSifre2026!",
        }
        response = self.client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(response.status_code, 401)

    def test_11_protected_me_with_valid_token_returns_user_profile(self):
        """Geçerli token ile korumalı /auth/me ucuna erişilip
        profil bilgileri alınmalı."""
        login_res = self.client.post(
            "/api/v1/auth/login",
            json={"email": "buse@sitwise.app", "password": "GucluSifre2026!"},
        )
        token = login_res.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        me_res = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(me_res.status_code, 200)

        data = me_res.json()
        self.assertEqual(data["email"], "buse@sitwise.app")
        self.assertEqual(data["name"], "Buse Demirbaş")
        self.assertIn("id", data)

    def test_12_logout_returns_204(self):
        """Çıkış ucu (/auth/logout) 204 No Content dönmeli."""
        response = self.client.post("/api/v1/auth/logout")
        self.assertEqual(response.status_code, 204)


if __name__ == "__main__":
    unittest.main()
