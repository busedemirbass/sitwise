"""
SW-031: Sahte Veri Üreteci (Mock / Seed Data Generator).
Kabul Kriteri: Tek komutla DB doluyor.

Geliştirme ve test ortamları için gerçekçi kullanıcı, oturum,
ergonomi metrik örnekleri, kalibrasyon, uyarı ve günlük özet verisi üretir.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import random

from sqlalchemy.orm import Session

from core.security import hash_password
from models.alert import Alert, AlertFeedback
from models.calibration_profile import CalibrationProfile
from models.daily_summary import DailySummary
from models.fatigue_report import FatigueReport
from models.metric_sample import MetricSample
from models.session import WorkSession
from models.threshold import UserThreshold
from models.user import User

DEMO_USERS = [
    {
        "name": "Demo Kullanıcı",
        "email": "demo@sitwise.app",
        "password": "Password123!",
    },
    {
        "name": "Buse Demirbaş",
        "email": "buse@sitwise.app",
        "password": "Password123!",
    },
    {
        "name": "Ece Ergonomist",
        "email": "ece@sitwise.app",
        "password": "Password123!",
    },
]


def clear_seed_data(db: Session, only_demo_users: bool = True) -> None:
    """Mevcut seed verilerini ilişkisel sırayla temizler."""
    demo_emails = [u["email"] for u in DEMO_USERS]
    demo_user_ids = [
        u.id for u in db.query(User).filter(User.email.in_(demo_emails)).all()
    ]

    if only_demo_users and demo_user_ids:
        # Oturumlara bağlı kayıtlar
        demo_sessions = (
            db.query(WorkSession).filter(WorkSession.user_id.in_(demo_user_ids)).all()
        )
        session_ids = [s.id for s in demo_sessions]

        if session_ids:
            alerts = db.query(Alert).filter(Alert.session_id.in_(session_ids)).all()
            alert_ids = [a.id for a in alerts]
            if alert_ids:
                db.query(AlertFeedback).filter(
                    AlertFeedback.alert_id.in_(alert_ids)
                ).delete(synchronize_session=False)
            db.query(Alert).filter(Alert.session_id.in_(session_ids)).delete(
                synchronize_session=False
            )
            db.query(MetricSample).filter(
                MetricSample.session_id.in_(session_ids)
            ).delete(synchronize_session=False)
            db.query(WorkSession).filter(WorkSession.id.in_(session_ids)).delete(
                synchronize_session=False
            )

        db.query(DailySummary).filter(DailySummary.user_id.in_(demo_user_ids)).delete(
            synchronize_session=False
        )
        db.query(FatigueReport).filter(FatigueReport.user_id.in_(demo_user_ids)).delete(
            synchronize_session=False
        )
        db.query(UserThreshold).filter(UserThreshold.user_id.in_(demo_user_ids)).delete(
            synchronize_session=False
        )
        db.query(CalibrationProfile).filter(
            CalibrationProfile.user_id.in_(demo_user_ids)
        ).delete(synchronize_session=False)
        db.query(User).filter(User.id.in_(demo_user_ids)).delete(
            synchronize_session=False
        )
    elif not only_demo_users:
        db.query(AlertFeedback).delete()
        db.query(Alert).delete()
        db.query(MetricSample).delete()
        db.query(WorkSession).delete()
        db.query(DailySummary).delete()
        db.query(FatigueReport).delete()
        db.query(UserThreshold).delete()
        db.query(CalibrationProfile).delete()
        db.query(User).delete()

    db.commit()


def seed_database(
    db: Session,
    days: int = 7,
    reset: bool = False,
    seed_value: int | None = 42,
) -> dict[str, int]:
    """Veritabanını gerçekçi sahte veriler ile doldurur.

    Args:
        db: SQLAlchemy veritabanı oturumu.
        days: Geriye dönük kaç günlük veri oluşturulacağı.
        reset: True ise mevcut demo verilerini temizleyip yeniden üretir.
        seed_value: Tekrarlanabilir rastgelelik için tohum.

    Returns:
        Üretilen varlıkların sayılarını içeren özet sözlük.
    """
    if seed_value is not None:
        random.seed(seed_value)

    if reset:
        clear_seed_data(db, only_demo_users=True)

    counts = {
        "users": 0,
        "calibration_profiles": 0,
        "thresholds": 0,
        "sessions": 0,
        "metric_samples": 0,
        "alerts": 0,
        "alert_feedbacks": 0,
        "daily_summaries": 0,
        "fatigue_reports": 0,
    }

    now = datetime.now(timezone.utc)
    today = now.date()

    created_users: list[User] = []
    for user_info in DEMO_USERS:
        existing = db.query(User).filter(User.email == user_info["email"]).first()
        if existing:
            created_users.append(existing)
            continue

        user = User(
            name=user_info["name"],
            email=user_info["email"],
            password_hash=hash_password(user_info["password"]),
            is_active=True,
            created_at=now - timedelta(days=days + 1),
        )
        db.add(user)
        db.flush()
        created_users.append(user)
        counts["users"] += 1

    for user in created_users:
        # 1. Kalibrasyon Profili
        calib_exists = (
            db.query(CalibrationProfile)
            .filter(CalibrationProfile.user_id == user.id)
            .first()
        )
        if not calib_exists:
            calib = CalibrationProfile(
                user_id=user.id,
                neck_mean=round(random.uniform(0.36, 0.40), 3),
                neck_std=round(random.uniform(0.03, 0.05), 3),
                shoulder_mean=round(random.uniform(-0.5, 0.5), 2),
                shoulder_std=round(random.uniform(0.02, 0.04), 3),
                distance_cm=round(random.uniform(56.0, 62.0), 1),
                created_at=now - timedelta(days=days),
            )
            db.add(calib)
            counts["calibration_profiles"] += 1

        # 2. Eşik Değerleri
        thresholds_data = [
            ("neck_ratio", 0.55),
            ("shoulder_tilt", 5.0),
            ("distance_cm", 45.0),
            ("blinks_per_min", 12.0),
        ]
        for metric, val in thresholds_data:
            t_exists = (
                db.query(UserThreshold)
                .filter(
                    UserThreshold.user_id == user.id,
                    UserThreshold.metric == metric,
                )
                .first()
            )
            if not t_exists:
                t = UserThreshold(
                    user_id=user.id,
                    metric=metric,
                    value=val,
                    updated_at=now - timedelta(days=days),
                )
                db.add(t)
                counts["thresholds"] += 1

        # 3. Günlük Oturumlar ve Metrikler
        for day_idx in range(days):
            target_date = today - timedelta(days=day_idx)

            # Günlük özet (DailySummary)
            summary_exists = (
                db.query(DailySummary)
                .filter(
                    DailySummary.user_id == user.id,
                    DailySummary.date == target_date,
                )
                .first()
            )
            if not summary_exists:
                summary = DailySummary(
                    user_id=user.id,
                    date=target_date,
                    score=random.randint(72, 95),
                    good_minutes=random.randint(180, 320),
                    alert_count=random.randint(2, 10),
                    avg_blink=round(random.uniform(14.0, 20.0), 1),
                    created_at=datetime.combine(
                        target_date, datetime.min.time(), tzinfo=timezone.utc
                    )
                    + timedelta(hours=18),
                )
                db.add(summary)
                counts["daily_summaries"] += 1

            # Yorgunluk Raporu (FatigueReport)
            fatigue_exists = (
                db.query(FatigueReport)
                .filter(
                    FatigueReport.user_id == user.id,
                    FatigueReport.date == target_date,
                )
                .first()
            )
            if not fatigue_exists:
                fatigue = FatigueReport(
                    user_id=user.id,
                    date=target_date,
                    score=random.randint(2, 4),
                    created_at=datetime.combine(
                        target_date, datetime.min.time(), tzinfo=timezone.utc
                    )
                    + timedelta(hours=18, minutes=15),
                )
                db.add(fatigue)
                counts["fatigue_reports"] += 1

            # Günde 1-2 çalışma oturumu
            session_times = [
                (
                    datetime.combine(
                        target_date, datetime.min.time(), tzinfo=timezone.utc
                    )
                    + timedelta(hours=9, minutes=30),
                    timedelta(hours=2, minutes=30),
                ),
                (
                    datetime.combine(
                        target_date, datetime.min.time(), tzinfo=timezone.utc
                    )
                    + timedelta(hours=14),
                    timedelta(hours=3),
                ),
            ]

            for s_start, s_duration in session_times:
                s_end = s_start + s_duration
                if s_start > now:
                    continue
                if s_end > now:
                    s_end = now

                session = WorkSession(
                    user_id=user.id,
                    started_at=s_start,
                    ended_at=s_end,
                    device="integrated_webcam",
                )
                db.add(session)
                db.flush()
                counts["sessions"] += 1

                # Her oturum için periyodik metrik örnekleri
                sample_time = s_start
                while sample_time < s_end:
                    roll = random.random()
                    if roll < 0.78:
                        neck = round(random.uniform(0.32, 0.44), 3)
                        shoulder = round(random.uniform(-1.5, 1.5), 2)
                        distance = round(random.uniform(55.0, 68.0), 1)
                        blinks = random.randint(15, 22)
                        state = "good"
                    elif roll < 0.92:
                        neck = round(random.uniform(0.48, 0.58), 3)
                        shoulder = round(
                            random.uniform(2.5, 5.0) * random.choice([1, -1]), 2
                        )
                        distance = round(random.uniform(43.0, 49.0), 1)
                        blinks = random.randint(10, 13)
                        state = "warning"
                    else:
                        neck = round(random.uniform(0.65, 0.85), 3)
                        shoulder = round(
                            random.uniform(6.0, 10.0) * random.choice([1, -1]),
                            2,
                        )
                        distance = round(random.uniform(32.0, 40.0), 1)
                        blinks = random.randint(6, 9)
                        state = "bad"

                    sample = MetricSample(
                        session_id=session.id,
                        ts=sample_time,
                        neck_ratio=neck,
                        shoulder_tilt=shoulder,
                        distance_cm=distance,
                        blinks_per_min=blinks,
                        state=state,
                    )
                    db.add(sample)
                    counts["metric_samples"] += 1

                    # Kötü duruşta uyarı üret
                    if state == "bad" and random.random() < 0.65:
                        alert_type = random.choice(
                            ["posture", "eye_fatigue", "distance"]
                        )
                        severity = random.choice(["medium", "high"])
                        alert = Alert(
                            session_id=session.id,
                            ts=sample_time,
                            type=alert_type,
                            severity=severity,
                        )
                        db.add(alert)
                        db.flush()
                        counts["alerts"] += 1

                        if random.random() < 0.5:
                            feedback = AlertFeedback(
                                alert_id=alert.id,
                                is_false=random.random() < 0.25,
                                created_at=sample_time + timedelta(seconds=20),
                            )
                            db.add(feedback)
                            counts["alert_feedbacks"] += 1

                    sample_time += timedelta(minutes=10)

    db.commit()
    return counts
