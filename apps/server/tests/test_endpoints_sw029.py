"""
SW-029 Uç Noktaları Test Paketi: /sessions, /metrics, /calibration
Kabul Kriteri: Hatalı JSON 422
"""

from __future__ import annotations

from datetime import datetime, timezone
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.security import create_access_token, hash_password
from db.base import Base
from db.session import get_db
from main import app
import models  # noqa: F401
from models.user import User


class TestEndpointsSW029(unittest.TestCase):
    """SW-029 /sessions, /metrics, /calibration uç noktaları testleri."""

    @classmethod
    def setUpClass(cls):
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
        app.dependency_overrides.clear()
        Base.metadata.drop_all(cls.engine)

    def setUp(self):
        self.db = self.SessionLocal()
        # Test kullanıcısı oluştur
        self.user = User(
            name="Test User",
            email="testuser@sitwise.app",
            password_hash=hash_password("Password123!"),
            is_active=True,
        )
        self.db.add(self.user)
        self.db.commit()
        self.db.refresh(self.user)

        self.token = create_access_token(
            {"sub": str(self.user.id), "email": self.user.email}
        )
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def tearDown(self):
        self.db.query(models.MetricSample).delete()
        self.db.query(models.WorkSession).delete()
        self.db.query(models.CalibrationProfile).delete()
        self.db.query(models.User).delete()
        self.db.commit()
        self.db.close()

    # -----------------------------------------------------------------------
    # Kabul Kriteri: Hatalı JSON -> 422 Unprocessable Entity
    # -----------------------------------------------------------------------

    def test_sessions_invalid_json_returns_422(self):
        """Hatalı /sessions isteği 422 dönmelidir."""
        # device boş dize olduğunda (min_length=1 kısıtlaması)
        res = self.client.post(
            "/api/v1/sessions/", json={"device": ""}, headers=self.headers
        )
        self.assertEqual(res.status_code, 422)

    def test_metrics_invalid_json_returns_422(self):
        """Hatalı /metrics/ingest isteği 422 dönmelidir."""
        # 1. Eksik session_id
        res = self.client.post(
            "/api/v1/metrics/ingest",
            json={"samples": []},
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 422)

        # 2. Boş samples listesi (min_length=1)
        res = self.client.post(
            "/api/v1/metrics/ingest",
            json={"session_id": "some-id", "samples": []},
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 422)

        # 3. Geçersiz neck_ratio (> 2.0)
        res = self.client.post(
            "/api/v1/metrics/ingest",
            json={
                "session_id": "some-id",
                "samples": [
                    {
                        "ts": "2026-10-23T12:00:00Z",
                        "neck_ratio": 3.5,  # Geçersiz
                        "shoulder_tilt": 0.0,
                        "distance_cm": 50.0,
                        "blinks_per_min": 15,
                        "state": "good",
                    }
                ],
            },
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 422)

        # 4. Geçersiz distance_cm (< 10.0)
        res = self.client.post(
            "/api/v1/metrics/ingest",
            json={
                "session_id": "some-id",
                "samples": [
                    {
                        "ts": "2026-10-23T12:00:00Z",
                        "neck_ratio": 0.5,
                        "shoulder_tilt": 0.0,
                        "distance_cm": 5.0,  # Geçersiz
                        "blinks_per_min": 15,
                        "state": "good",
                    }
                ],
            },
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 422)

        # 5. Sayısal olmayan tip (örneğin neck_ratio="invalid")
        res = self.client.post(
            "/api/v1/metrics/ingest",
            json={
                "session_id": "some-id",
                "samples": [
                    {
                        "ts": "2026-10-23T12:00:00Z",
                        "neck_ratio": "invalid",
                        "shoulder_tilt": 0.0,
                        "distance_cm": 50.0,
                        "blinks_per_min": 15,
                        "state": "good",
                    }
                ],
            },
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 422)

    def test_calibration_invalid_json_returns_422(self):
        """Hatalı /calibration isteği 422 dönmelidir."""
        # 1. Eksik zorunlu alanlar
        res = self.client.post(
            "/api/v1/calibration/",
            json={"neck_mean": 0.5},
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 422)

        # 2. Negatif standart sapma (neck_std < 0.0)
        res = self.client.post(
            "/api/v1/calibration/",
            json={
                "neck_mean": 0.5,
                "neck_std": -0.1,  # Geçersiz
                "shoulder_mean": 0.0,
                "shoulder_std": 0.02,
                "distance_cm": 55.0,
            },
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 422)

        # 3. Geçersiz mesafe (distance_cm > 200.0)
        res = self.client.post(
            "/api/v1/calibration/",
            json={
                "neck_mean": 0.5,
                "neck_std": 0.05,
                "shoulder_mean": 0.0,
                "shoulder_std": 0.02,
                "distance_cm": 350.0,  # Geçersiz
            },
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 422)

    # -----------------------------------------------------------------------
    # Başarılı Akış Testleri (Sessions, Metrics, Calibration)
    # -----------------------------------------------------------------------

    def test_sessions_flow(self):
        """Oturum başlatma, listeleme, detay ve bitirme başarılı akışı."""
        # 1. Oturum Başlat
        res = self.client.post(
            "/api/v1/sessions/",
            json={"device": "integrated_webcam"},
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        session_id = data["id"]
        self.assertEqual(data["device"], "integrated_webcam")
        self.assertIsNone(data["ended_at"])

        # 2. Oturum Detayını Al
        res_get = self.client.get(
            f"/api/v1/sessions/{session_id}", headers=self.headers
        )
        self.assertEqual(res_get.status_code, 200)
        self.assertEqual(res_get.json()["id"], session_id)

        # 3. Oturumları Listele
        res_list = self.client.get("/api/v1/sessions/", headers=self.headers)
        self.assertEqual(res_list.status_code, 200)
        self.assertEqual(res_list.json()["total"], 1)

        # 4. Oturumu Bitir
        res_end = self.client.patch(
            f"/api/v1/sessions/{session_id}/end", headers=self.headers
        )
        self.assertEqual(res_end.status_code, 200)
        self.assertIsNotNone(res_end.json()["ended_at"])

    def test_metrics_flow(self):
        """Metrik gönderimi ve sorgulama akışı."""
        # Önce oturum aç
        res_sess = self.client.post(
            "/api/v1/sessions/",
            json={"device": "webcam"},
            headers=self.headers,
        )
        session_id = res_sess.json()["id"]

        # Metrik gönder
        payload = {
            "session_id": session_id,
            "samples": [
                {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "neck_ratio": 0.42,
                    "shoulder_tilt": 1.5,
                    "distance_cm": 58.0,
                    "blinks_per_min": 18,
                    "state": "good",
                },
                {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "neck_ratio": 0.75,
                    "shoulder_tilt": 2.1,
                    "distance_cm": 45.0,
                    "blinks_per_min": 10,
                    "state": "warning",
                },
            ],
        }
        res_ingest = self.client.post(
            "/api/v1/metrics/ingest",
            json=payload,
            headers=self.headers,
        )
        self.assertEqual(res_ingest.status_code, 202)
        self.assertEqual(res_ingest.json()["accepted"], 2)

        # Metrikleri sorgula
        res_list = self.client.get(
            f"/api/v1/metrics/?session_id={session_id}",
            headers=self.headers,
        )
        self.assertEqual(res_list.status_code, 200)
        self.assertEqual(res_list.json()["total"], 2)

    def test_calibration_flow(self):
        """Kalibrasyon profili oluşturma, son profili alma ve listeleme."""
        payload = {
            "neck_mean": 0.35,
            "neck_std": 0.04,
            "shoulder_mean": 0.5,
            "shoulder_std": 0.03,
            "distance_cm": 60.0,
        }
        # 1. Oluştur
        res = self.client.post(
            "/api/v1/calibration/",
            json=payload,
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        calib_id = data["id"]
        self.assertEqual(data["distance_cm"], 60.0)

        # 2. Son Kalibrasyonu Getir
        res_latest = self.client.get("/api/v1/calibration/latest", headers=self.headers)
        self.assertEqual(res_latest.status_code, 200)
        self.assertEqual(res_latest.json()["id"], calib_id)

        # 3. Listele
        res_list = self.client.get("/api/v1/calibration/", headers=self.headers)
        self.assertEqual(res_list.status_code, 200)
        self.assertEqual(res_list.json()["total"], 1)

    def test_unauthorized_endpoints_return_401(self):
        """Token olmadan istekler 401 dönmelidir."""
        self.assertEqual(
            self.client.post("/api/v1/sessions/", json={}).status_code, 401
        )
        self.assertEqual(self.client.get("/api/v1/sessions/").status_code, 401)
        self.assertEqual(
            self.client.post("/api/v1/metrics/ingest", json={}).status_code, 401
        )
        self.assertEqual(
            self.client.get("/api/v1/calibration/latest").status_code, 401
        )
