"""
Metrics service — ergonomi metrik örnekleri iş mantığı katmanı.
SW-029 / SW-030: docs/uml/class-server.md referans alınmıştır.
"""

from __future__ import annotations

from datetime import datetime
import uuid

from fastapi import HTTPException, status

from models.metric_sample import MetricSample
from repositories.metric_repository import MetricRepository
from repositories.session_repository import SessionRepository


class MetricsService:
    """Ergonometri metriklerini kabul eden ve sorgulayan servis sınıfı."""

    def __init__(
        self,
        metric_repo: MetricRepository,
        session_repo: SessionRepository,
    ) -> None:
        self.metric_repo = metric_repo
        self.session_repo = session_repo

    def ingest(
        self,
        session_id: uuid.UUID | str,
        user_id: uuid.UUID | str,
        samples: list[dict],
    ) -> int:
        """Toplu metrik örneğini kabul eder ve kaydeder."""
        session = self.session_repo.get_by_id_and_user(
            session_id=session_id, user_id=user_id
        )
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Oturum bulunamadı veya erişim yetkiniz yok.",
            )

        if not samples:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="En az bir metrik örneği gönderilmelidir.",
            )

        saved = self.metric_repo.add_batch(session_id=session.id, samples=samples)
        return len(saved)

    def get_metrics(
        self,
        session_id: uuid.UUID | str,
        user_id: uuid.UUID | str,
        from_ts: datetime | None = None,
        to_ts: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[MetricSample], int]:
        """Oturuma ait metrik örneklerini listeler."""
        session = self.session_repo.get_by_id_and_user(
            session_id=session_id, user_id=user_id
        )
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Oturum bulunamadı veya erişim yetkiniz yok.",
            )

        return self.metric_repo.get_by_session(
            session_id=session.id,
            from_ts=from_ts,
            to_ts=to_ts,
            limit=limit,
            offset=offset,
        )
