"""
SQLAlchemy modelleri birim testleri (SW-020).
Bölüm 4.5 şeması altındaki tüm 9 modelin CRUD ve ilişki testleri.
"""

from datetime import date
import unittest
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base
from models import (
    Alert,
    AlertFeedback,
    CalibrationProfile,
    DailySummary,
    FatigueReport,
    MetricSample,
    User,
    UserThreshold,
    WorkSession,
)


class TestModels(unittest.TestCase):
    """Bölüm 4.5 SQLAlchemy modelleri test paketi."""

    @classmethod
    def setUpClass(cls):
        """Bellek içi SQLite veritabanı ve oturum fabrikası oluştur."""
        cls.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        """Her test için yeni bir oturum aç."""
        self.session = self.Session()

    def tearDown(self):
        """Her test sonrası oturumu kapat ve temizle."""
        self.session.rollback()
        self.session.close()

    def test_create_user(self):
        """Kullanıcı oluşturma ve sorgulama testi."""
        user = User(
            id=uuid.uuid4(),
            name="Test User",
            email="test@sitwise.app",
            password_hash="hashed_pw_123",
        )
        self.session.add(user)
        self.session.commit()

        fetched = self.session.query(User).filter_by(email="test@sitwise.app").first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, "Test User")
        self.assertTrue(fetched.is_active)
        self.assertIsNotNone(fetched.created_at)

    def test_session_and_samples_relationship(self):
        """Oturum ve metrik örnekleri ilişkisi testi."""
        user = User(
            id=uuid.uuid4(),
            name="Session Owner",
            email="session@sitwise.app",
            password_hash="hashed_pw_456",
        )
        self.session.add(user)
        self.session.commit()

        work_session = WorkSession(
            id=uuid.uuid4(),
            user_id=user.id,
            device="webcam-logitech",
        )
        self.session.add(work_session)
        self.session.commit()

        sample = MetricSample(
            session_id=work_session.id,
            neck_ratio=1.05,
            shoulder_tilt=2.3,
            distance_cm=62.0,
            blinks_per_min=18,
            state="good",
        )
        self.session.add(sample)
        self.session.commit()

        # Oturum üzerinden örneğe erişim
        self.assertEqual(len(work_session.metric_samples), 1)
        self.assertEqual(work_session.metric_samples[0].state, "good")
        self.assertEqual(work_session.metric_samples[0].session_id, work_session.id)

    def test_alert_and_feedback_relationship(self):
        """Uyarı ve geri bildirim ilişkisi testi."""
        user = User(
            id=uuid.uuid4(),
            name="Alert User",
            email="alert@sitwise.app",
            password_hash="hashed_pw_789",
        )
        self.session.add(user)
        self.session.commit()

        work_session = WorkSession(id=uuid.uuid4(), user_id=user.id)
        self.session.add(work_session)
        self.session.commit()

        alert = Alert(
            id=uuid.uuid4(),
            session_id=work_session.id,
            type="posture",
            severity="medium",
        )
        self.session.add(alert)
        self.session.commit()

        feedback = AlertFeedback(
            id=uuid.uuid4(),
            alert_id=alert.id,
            is_false=True,
        )
        self.session.add(feedback)
        self.session.commit()

        self.assertIsNotNone(alert.feedback)
        self.assertTrue(alert.feedback.is_false)
        self.assertEqual(alert.feedback.alert_id, alert.id)

    def test_calibration_profile(self):
        """Kalibrasyon profili oluşturma testi."""
        user = User(
            id=uuid.uuid4(),
            name="Calib User",
            email="calib@sitwise.app",
            password_hash="pw",
        )
        self.session.add(user)
        self.session.commit()

        profile = CalibrationProfile(
            id=uuid.uuid4(),
            user_id=user.id,
            neck_mean=1.02,
            neck_std=0.04,
            shoulder_mean=0.1,
            shoulder_std=0.5,
            distance_cm=65.0,
        )
        self.session.add(profile)
        self.session.commit()

        fetched = (
            self.session.query(CalibrationProfile).filter_by(user_id=user.id).first()
        )
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.distance_cm, 65.0)
        self.assertEqual(len(user.calibration_profiles), 1)

    def test_user_threshold(self):
        """Kullanıcı metrik eşik değeri testi."""
        user = User(
            id=uuid.uuid4(),
            name="Threshold User",
            email="threshold@sitwise.app",
            password_hash="pw",
        )
        self.session.add(user)
        self.session.commit()

        threshold = UserThreshold(
            id=uuid.uuid4(),
            user_id=user.id,
            metric="neck_ratio",
            value=1.15,
        )
        self.session.add(threshold)
        self.session.commit()

        fetched = self.session.query(UserThreshold).filter_by(user_id=user.id).first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.metric, "neck_ratio")
        self.assertEqual(fetched.value, 1.15)

    def test_daily_summary(self):
        """Günlük özet oluşturma testi."""
        user = User(
            id=uuid.uuid4(),
            name="Summary User",
            email="summary@sitwise.app",
            password_hash="pw",
        )
        self.session.add(user)
        self.session.commit()

        summary = DailySummary(
            id=uuid.uuid4(),
            user_id=user.id,
            date=date(2026, 10, 7),
            score=88,
            good_minutes=240,
            alert_count=3,
            avg_blink=19.5,
        )
        self.session.add(summary)
        self.session.commit()

        fetched = self.session.query(DailySummary).filter_by(user_id=user.id).first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.score, 88)
        self.assertEqual(fetched.good_minutes, 240)

    def test_fatigue_report(self):
        """Yorgunluk raporu oluşturma testi."""
        user = User(
            id=uuid.uuid4(),
            name="Fatigue User",
            email="fatigue@sitwise.app",
            password_hash="pw",
        )
        self.session.add(user)
        self.session.commit()

        report = FatigueReport(
            id=uuid.uuid4(),
            user_id=user.id,
            date=date(2026, 10, 7),
            score=4,
        )
        self.session.add(report)
        self.session.commit()

        fetched = self.session.query(FatigueReport).filter_by(user_id=user.id).first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.score, 4)
        self.assertEqual(len(user.fatigue_reports), 1)


if __name__ == "__main__":
    unittest.main()
