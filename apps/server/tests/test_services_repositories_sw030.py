"""
SW-030: Repository Katmanı ve Servis Testleri.
Kabul Kriteri: Servis katmanında %70 test kapsamı (Coverage >= 70%).
"""

from __future__ import annotations

from datetime import datetime, timezone
import unittest
import uuid

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.base import Base
import models  # noqa: F401
from repositories.calibration_repository import CalibrationRepository
from repositories.metric_repository import MetricRepository
from repositories.session_repository import SessionRepository
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from services.calibration_service import CalibrationService
from services.metrics_service import MetricsService
from services.session_service import SessionService


class TestServicesAndRepositoriesSW030(unittest.TestCase):
    """Servis ve Repository katmanları kapsamlı birim test paketi."""

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

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.engine)

    def setUp(self):
        self.db = self.SessionLocal()
        self.user_repo = UserRepository(self.db)
        self.session_repo = SessionRepository(self.db)
        self.metric_repo = MetricRepository(self.db)
        self.calibration_repo = CalibrationRepository(self.db)

        self.auth_service = AuthService(self.user_repo)
        self.session_service = SessionService(self.session_repo)
        self.metrics_service = MetricsService(self.metric_repo, self.session_repo)
        self.calibration_service = CalibrationService(self.calibration_repo)

        # Temel kullanıcı kaydı
        token = self.auth_service.register(
            name="Alice Ergonomics",
            email="alice@sitwise.app",
            password="StrongPassword123!",
        )
        self.user = self.auth_service.verify_token(token)

    def tearDown(self):
        self.db.query(models.MetricSample).delete()
        self.db.query(models.WorkSession).delete()
        self.db.query(models.CalibrationProfile).delete()
        self.db.query(models.User).delete()
        self.db.commit()
        self.db.close()

    # -----------------------------------------------------------------------
    # AuthService & UserRepository Testleri
    # -----------------------------------------------------------------------

    def test_auth_service_duplicate_email_raises_400(self):
        with self.assertRaises(HTTPException) as ctx:
            self.auth_service.register(
                name="Duplicate",
                email="alice@sitwise.app",
                password="AnotherPassword123!",
            )
        self.assertEqual(ctx.exception.status_code, 400)

    def test_auth_service_login_success_and_failure(self):
        # Başarılı giriş
        token = self.auth_service.login("alice@sitwise.app", "StrongPassword123!")
        self.assertIsInstance(token, str)

        # Hatalı şifre -> 401
        with self.assertRaises(HTTPException) as ctx:
            self.auth_service.login("alice@sitwise.app", "WrongPassword!")
        self.assertEqual(ctx.exception.status_code, 401)

        # Bulunamayan kullanıcı -> 401
        with self.assertRaises(HTTPException) as ctx2:
            self.auth_service.login("nonexistent@sitwise.app", "Password123!")
        self.assertEqual(ctx2.exception.status_code, 401)

    def test_auth_service_verify_token_invalid_or_inactive(self):
        # Geçersiz token
        with self.assertRaises(HTTPException) as ctx:
            self.auth_service.verify_token("invalid.token.here")
        self.assertEqual(ctx.exception.status_code, 401)

        # Pasif kullanıcı
        valid_token = self.auth_service.login("alice@sitwise.app", "StrongPassword123!")
        self.user.is_active = False
        self.db.commit()
        with self.assertRaises(HTTPException) as ctx2:
            self.auth_service.verify_token(valid_token)
        self.assertEqual(ctx2.exception.status_code, 401)

        # Pasif kullanıcı ile giriş denemesi -> 400
        with self.assertRaises(HTTPException) as ctx3:
            self.auth_service.login("alice@sitwise.app", "StrongPassword123!")
        self.assertEqual(ctx3.exception.status_code, 400)

    def test_user_repository_get_by_id_edge_cases(self):
        # Geçersiz UUID string
        self.assertIsNone(self.user_repo.get_by_id("not-a-uuid"))
        # Var olmayan UUID
        self.assertIsNone(self.user_repo.get_by_id(uuid.uuid4()))
        # Var olan kullanıcı
        self.assertIsNotNone(self.user_repo.get_by_id(str(self.user.id)))

    # -----------------------------------------------------------------------
    # SessionService & SessionRepository Testleri
    # -----------------------------------------------------------------------

    def test_session_lifecycle(self):
        session = self.session_service.start_session(
            user_id=self.user.id, device="external_4k_webcam"
        )
        self.assertEqual(session.device, "external_4k_webcam")
        self.assertIsNone(session.ended_at)

        # Oturumu getir
        fetched = self.session_service.get_session(
            session_id=session.id, user_id=self.user.id
        )
        self.assertEqual(fetched.id, session.id)

        # Oturumları listele
        sessions, total = self.session_service.list_sessions(
            user_id=self.user.id, limit=10, offset=0
        )
        self.assertEqual(total, 1)
        self.assertEqual(len(sessions), 1)

        # Oturumu sonlandır
        ended = self.session_service.end_session(
            session_id=session.id, user_id=self.user.id
        )
        self.assertIsNotNone(ended.ended_at)

        # İkinci kez sonlandırıldığında hata vermez, mevcut ended_at korunur
        ended2 = self.session_service.end_session(
            session_id=session.id, user_id=self.user.id
        )
        self.assertEqual(ended.ended_at, ended2.ended_at)

    def test_session_service_not_found_raises_404(self):
        fake_id = str(uuid.uuid4())
        with self.assertRaises(HTTPException) as ctx:
            self.session_service.get_session(session_id=fake_id, user_id=self.user.id)
        self.assertEqual(ctx.exception.status_code, 404)

        with self.assertRaises(HTTPException) as ctx2:
            self.session_service.end_session(session_id=fake_id, user_id=self.user.id)
        self.assertEqual(ctx2.exception.status_code, 404)

    def test_session_repository_invalid_uuid(self):
        self.assertIsNone(
            self.session_repo.get_by_id_and_user("invalid-id", "invalid-user")
        )
        sess, total = self.session_repo.list_by_user("invalid-user")
        self.assertEqual(sess, [])
        self.assertEqual(total, 0)

    # -----------------------------------------------------------------------
    # MetricsService & MetricRepository Testleri
    # -----------------------------------------------------------------------

    def test_metrics_service_ingest_and_query(self):
        session = self.session_service.start_session(
            user_id=self.user.id, device="laptop_cam"
        )
        samples = [
            {
                "ts": datetime(2026, 10, 23, 10, 0, 0, tzinfo=timezone.utc),
                "neck_ratio": 0.35,
                "shoulder_tilt": 0.5,
                "distance_cm": 62.0,
                "blinks_per_min": 17,
                "state": "good",
            },
            {
                "ts": datetime(2026, 10, 23, 10, 1, 0, tzinfo=timezone.utc),
                "neck_ratio": 0.85,
                "shoulder_tilt": -1.2,
                "distance_cm": 42.0,
                "blinks_per_min": 8,
                "state": "bad",
            },
        ]

        count = self.metrics_service.ingest(
            session_id=session.id, user_id=self.user.id, samples=samples
        )
        self.assertEqual(count, 2)

        # Tüm metrikleri sorgula
        retrieved, total = self.metrics_service.get_metrics(
            session_id=session.id, user_id=self.user.id
        )
        self.assertEqual(total, 2)
        self.assertEqual(len(retrieved), 2)
        self.assertEqual(retrieved[0].state, "good")
        self.assertEqual(retrieved[1].state, "bad")

        # Zaman filtreli sorgula
        filtered, f_total = self.metrics_service.get_metrics(
            session_id=session.id,
            user_id=self.user.id,
            from_ts=datetime(2026, 10, 23, 10, 0, 30, tzinfo=timezone.utc),
        )
        self.assertEqual(f_total, 1)
        self.assertEqual(filtered[0].state, "bad")

    def test_metrics_service_errors(self):
        session = self.session_service.start_session(user_id=self.user.id, device="cam")

        # Boş liste gönderimi -> 400
        with self.assertRaises(HTTPException) as ctx:
            self.metrics_service.ingest(
                session_id=session.id, user_id=self.user.id, samples=[]
            )
        self.assertEqual(ctx.exception.status_code, 400)

        # Var olmayan oturuma gönderim -> 404
        fake_sess = str(uuid.uuid4())
        with self.assertRaises(HTTPException) as ctx2:
            self.metrics_service.ingest(
                session_id=fake_sess,
                user_id=self.user.id,
                samples=[
                    {
                        "ts": datetime.now(timezone.utc),
                        "neck_ratio": 0.4,
                        "shoulder_tilt": 0.0,
                        "distance_cm": 50.0,
                        "blinks_per_min": 15,
                        "state": "good",
                    }
                ],
            )
        self.assertEqual(ctx2.exception.status_code, 404)

        # Var olmayan oturumdan metrik sorgulama -> 404
        with self.assertRaises(HTTPException) as ctx3:
            self.metrics_service.get_metrics(session_id=fake_sess, user_id=self.user.id)
        self.assertEqual(ctx3.exception.status_code, 404)

    def test_metric_repository_invalid_uuid(self):
        items, count = self.metric_repo.get_by_session("not-a-valid-uuid")
        self.assertEqual(items, [])
        self.assertEqual(count, 0)

    # -----------------------------------------------------------------------
    # CalibrationService & CalibrationRepository Testleri
    # -----------------------------------------------------------------------

    def test_calibration_service_lifecycle(self):
        # Henüz profil yokken get_latest -> 404
        with self.assertRaises(HTTPException) as ctx:
            self.calibration_service.get_latest(user_id=self.user.id)
        self.assertEqual(ctx.exception.status_code, 404)

        # İlk kalibrasyonu oluştur
        p1 = self.calibration_service.create_calibration(
            user_id=self.user.id,
            neck_mean=0.30,
            neck_std=0.04,
            shoulder_mean=0.2,
            shoulder_std=0.03,
            distance_cm=58.0,
        )
        self.assertEqual(p1.distance_cm, 58.0)

        # İkinci kalibrasyonu oluştur
        p2 = self.calibration_service.create_calibration(
            user_id=self.user.id,
            neck_mean=0.32,
            neck_std=0.05,
            shoulder_mean=0.1,
            shoulder_std=0.02,
            distance_cm=62.0,
        )

        # get_latest en günceli (p2) dönmelidir
        latest = self.calibration_service.get_latest(user_id=self.user.id)
        self.assertEqual(latest.id, p2.id)
        self.assertEqual(latest.distance_cm, 62.0)

        # listele
        profiles = self.calibration_service.list_calibrations(user_id=self.user.id)
        self.assertEqual(len(profiles), 2)

    def test_calibration_repository_invalid_uuid(self):
        self.assertIsNone(self.calibration_repo.get_latest_by_user("invalid-uuid"))
        self.assertEqual(self.calibration_repo.list_by_user("invalid-uuid"), [])
