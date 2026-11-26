"""
SW-031 Test Paketi: Sahte Veri Üreteci (Mock / Seed Data Generator).
Kabul Kriteri: Tek komutla DB doluyor.
"""

from __future__ import annotations

import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.security import verify_password
from db.base import Base
from db.seed import clear_seed_data, seed_database
from models.alert import Alert, AlertFeedback
from models.calibration_profile import CalibrationProfile
from models.daily_summary import DailySummary
from models.fatigue_report import FatigueReport
from models.metric_sample import MetricSample
from models.session import WorkSession
from models.threshold import UserThreshold
from models.user import User


class TestSeedSW031(unittest.TestCase):
    """SW-031 Sahte Veri Üreteci birim testleri."""

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

    def tearDown(self):
        clear_seed_data(self.db, only_demo_users=False)
        self.db.close()

    def test_seed_creates_expected_data(self):
        """seed_database fonksiyonunun tüm modelleri başarıyla doldurduğunu doğrular."""
        stats = seed_database(self.db, days=3, reset=False, seed_value=123)

        # 1. Kullanıcılar
        self.assertGreater(stats["users"], 0)
        users = self.db.query(User).all()
        self.assertEqual(len(users), 3)

        demo_user = self.db.query(User).filter(User.email == "demo@sitwise.app").first()
        self.assertIsNotNone(demo_user)
        self.assertTrue(verify_password("Password123!", demo_user.password_hash))

        # 2. Kalibrasyon Profilleri
        calibs = self.db.query(CalibrationProfile).all()
        self.assertEqual(len(calibs), 3)
        for c in calibs:
            self.assertGreater(c.neck_std, 0.0)
            self.assertGreater(c.shoulder_std, 0.0)
            self.assertTrue(10.0 <= c.distance_cm <= 200.0)

        # 3. Eşik Değerleri
        thresholds = self.db.query(UserThreshold).all()
        self.assertGreaterEqual(len(thresholds), 12)  # 3 kullanıcı * 4 metrik

        # 4. Oturumlar ve Metrik Örnekleri
        sessions = self.db.query(WorkSession).all()
        self.assertGreater(len(sessions), 0)

        samples = self.db.query(MetricSample).all()
        self.assertGreater(len(samples), 0)

        # Check constraint sınır kontrolleri
        for s in samples:
            self.assertTrue(0.0 <= s.neck_ratio <= 2.0)
            self.assertTrue(-90.0 <= s.shoulder_tilt <= 90.0)
            self.assertTrue(10.0 <= s.distance_cm <= 200.0)
            self.assertTrue(0 <= s.blinks_per_min <= 60)
            self.assertIn(s.state, ["good", "warning", "bad"])

        # 5. Uyarılar ve Geri Bildirim
        alerts = self.db.query(Alert).all()
        self.assertGreaterEqual(len(alerts), 0)

        feedbacks = self.db.query(AlertFeedback).all()
        for f in feedbacks:
            self.assertIsInstance(f.is_false, bool)

        # 6. Günlük Özetler ve Yorgunluk Raporları
        summaries = self.db.query(DailySummary).all()
        self.assertGreater(len(summaries), 0)
        for sm in summaries:
            self.assertTrue(0 <= sm.score <= 100)
            self.assertGreaterEqual(sm.good_minutes, 0)
            self.assertGreaterEqual(sm.alert_count, 0)

        fatigues = self.db.query(FatigueReport).all()
        self.assertGreater(len(fatigues), 0)
        for fr in fatigues:
            self.assertTrue(1 <= fr.score <= 10)

    def test_seed_idempotent(self):
        """seed_database fonksiyonunun ardışık çağrımlarda hata vermediğini doğrular."""
        # İlk çalıştırma
        seed_database(self.db, days=2, reset=False, seed_value=42)
        initial_users = self.db.query(User).count()

        # İkinci çalıştırma (reset=False iken mevcut kullanıcıları korur)
        stats2 = seed_database(self.db, days=2, reset=False, seed_value=42)
        self.assertEqual(stats2["users"], 0)
        self.assertEqual(self.db.query(User).count(), initial_users)

    def test_seed_with_reset(self):
        """reset=True durumunda verilerin temizlenip yeniden
        üretildiğini doğrular.
        """
        seed_database(self.db, days=2, reset=False, seed_value=42)
        self.assertGreater(self.db.query(User).count(), 0)

        # reset=True ile yeniden çalıştır
        stats_reset = seed_database(self.db, days=2, reset=True, seed_value=42)
        self.assertGreater(stats_reset["users"], 0)
        self.assertEqual(self.db.query(User).count(), 3)
