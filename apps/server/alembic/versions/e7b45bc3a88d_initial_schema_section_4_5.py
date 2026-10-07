"""initial_schema_section_4_5

Revision ID: e7b45bc3a88d
Revises:
Create Date: 2026-10-07 20:43:01.043903
SW-020: SQLAlchemy models and Alembic migrations
Section 4.5 and docs/uml/er.md database schema.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e7b45bc3a88d"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all Section 4.5 database tables."""
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 2. calibration_profiles
    op.create_table(
        "calibration_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("neck_mean", sa.Float(), nullable=False),
        sa.Column("neck_std", sa.Float(), nullable=False),
        sa.Column("shoulder_mean", sa.Float(), nullable=False),
        sa.Column("shoulder_std", sa.Float(), nullable=False),
        sa.Column("distance_cm", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("neck_std >= 0.0", name="ck_calib_neck_std_positive"),
        sa.CheckConstraint(
            "shoulder_std >= 0.0", name="ck_calib_shoulder_std_positive"
        ),
        sa.CheckConstraint(
            "distance_cm >= 10.0 AND distance_cm <= 200.0",
            name="ck_calib_distance_cm_range",
        ),
    )
    op.create_index(
        "ix_calibration_profiles_user_id", "calibration_profiles", ["user_id"]
    )

    # 3. sessions
    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("device", sa.String(100), nullable=False, server_default="webcam"),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])

    # 4. metric_samples
    op.create_table(
        "metric_samples",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "ts",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("neck_ratio", sa.Float(), nullable=False),
        sa.Column("shoulder_tilt", sa.Float(), nullable=False),
        sa.Column("distance_cm", sa.Float(), nullable=False),
        sa.Column("blinks_per_min", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.CheckConstraint(
            "neck_ratio >= 0.0 AND neck_ratio <= 2.0", name="ck_neck_ratio_range"
        ),
        sa.CheckConstraint(
            "shoulder_tilt >= -90.0 AND shoulder_tilt <= 90.0",
            name="ck_shoulder_tilt_range",
        ),
        sa.CheckConstraint(
            "distance_cm >= 10.0 AND distance_cm <= 200.0", name="ck_distance_cm_range"
        ),
        sa.CheckConstraint(
            "blinks_per_min >= 0 AND blinks_per_min <= 60",
            name="ck_blinks_per_min_range",
        ),
    )
    op.create_index(
        "ix_metric_samples_session_ts", "metric_samples", ["session_id", "ts"]
    )

    # 5. alerts
    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "ts",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
    )
    op.create_index("ix_alerts_session_ts", "alerts", ["session_id", "ts"])

    # 6. alert_feedback
    op.create_table(
        "alert_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "alert_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("alerts.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("is_false", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_alert_feedback_alert_id", "alert_feedback", ["alert_id"])

    # 7. user_thresholds
    op.create_table(
        "user_thresholds",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("metric", sa.String(50), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("user_id", "metric", name="uq_user_thresholds_user_metric"),
    )
    op.create_index("ix_user_thresholds_user_id", "user_thresholds", ["user_id"])

    # 8. fatigue_reports
    op.create_table(
        "fatigue_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_fatigue_reports_user_id", "fatigue_reports", ["user_id"])
    op.create_index("ix_fatigue_reports_date", "fatigue_reports", ["date"])

    # 9. daily_summaries
    op.create_table(
        "daily_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("good_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("alert_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_blink", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("user_id", "date", name="uq_daily_summaries_user_date"),
        sa.CheckConstraint(
            "score >= 0 AND score <= 100", name="ck_daily_summary_score_range"
        ),
        sa.CheckConstraint("good_minutes >= 0", name="ck_daily_summary_good_minutes"),
        sa.CheckConstraint("alert_count >= 0", name="ck_daily_summary_alert_count"),
        sa.CheckConstraint(
            "avg_blink >= 0.0 AND avg_blink <= 60.0",
            name="ck_daily_summary_avg_blink_range",
        ),
    )
    op.create_index("ix_daily_summaries_user_id", "daily_summaries", ["user_id"])
    op.create_index("ix_daily_summaries_date", "daily_summaries", ["date"])


def downgrade() -> None:
    """Drop Section 4.5 database tables in reverse dependency order."""
    op.drop_table("daily_summaries")
    op.drop_table("fatigue_reports")
    op.drop_table("user_thresholds")
    op.drop_table("alert_feedback")
    op.drop_table("alerts")
    op.drop_table("metric_samples")
    op.drop_table("sessions")
    op.drop_table("calibration_profiles")
    op.drop_table("users")
