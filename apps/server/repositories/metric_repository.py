"""
Metric repository — ergonomi metrik örnekleri veri erişim katmanı.
SW-029 / SW-030: docs/uml/class-server.md referans alınmıştır.
"""

from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy.orm import Session

from models.metric_sample import MetricSample
from repositories.base import BaseRepository


class MetricRepository(BaseRepository[MetricSample]):
    """Ergonometri metrik örneklerine erişim sağlayan repository sınıfı."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, MetricSample)

    def _parse_uuid(self, val: uuid.UUID | str) -> uuid.UUID:
        if isinstance(val, str):
            return uuid.UUID(val)
        return val

    def add_batch(
        self, session_id: uuid.UUID | str, samples: list[dict]
    ) -> list[MetricSample]:
        """Bir oturuma ait toplu metrik örneklerini veritabanına ekler."""
        s_id = self._parse_uuid(session_id)
        entities: list[MetricSample] = []

        for item in samples:
            entity = MetricSample(
                session_id=s_id,
                ts=item["ts"],
                neck_ratio=item["neck_ratio"],
                shoulder_tilt=item["shoulder_tilt"],
                distance_cm=item["distance_cm"],
                blinks_per_min=item["blinks_per_min"],
                state=item["state"],
            )
            entities.append(entity)

        self.db.add_all(entities)
        self.db.commit()
        for ent in entities:
            self.db.refresh(ent)
        return entities

    def get_by_session(
        self,
        session_id: uuid.UUID | str,
        from_ts: datetime | None = None,
        to_ts: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[MetricSample], int]:
        """Oturuma ait metrik örneklerini zaman aralığına göre listeler."""
        try:
            s_id = self._parse_uuid(session_id)
        except (ValueError, AttributeError):
            return [], 0

        query = self.db.query(MetricSample).filter(MetricSample.session_id == s_id)
        if from_ts is not None:
            query = query.filter(MetricSample.ts >= from_ts)
        if to_ts is not None:
            query = query.filter(MetricSample.ts <= to_ts)

        total = query.count()
        samples = (
            query.order_by(MetricSample.ts.asc()).offset(offset).limit(limit).all()
        )
        return samples, total
