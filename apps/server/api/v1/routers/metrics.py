"""
Metrics router — ergonomi metrik örneklerini toplu gönderme ve sorgulama uçları.
SW-015 / SW-029: OpenAPI spesifikasyonu v1 ve uç nokta uygulaması.

Kural: Kamera kareleri asla gönderilmez; yalnızca sayısal özetler iletilir.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.deps import get_current_user
from db.session import get_db
from models.user import User
from repositories.metric_repository import MetricRepository
from repositories.session_repository import SessionRepository
from services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["Metrics"])


# ---------------------------------------------------------------------------
# Request / Response şemaları
# ---------------------------------------------------------------------------


class MetricSample(BaseModel):
    """Tek bir metrik örneği — istemcide hesaplanmış sayısal değerler."""

    ts: datetime = Field(..., description="Örnek zaman damgası (UTC)")
    neck_ratio: float = Field(..., ge=0.0, le=2.0, description="Boyun eğim oranı")
    shoulder_tilt: float = Field(
        ..., ge=-90.0, le=90.0, description="Omuz eğimi (derece)"
    )
    distance_cm: float = Field(
        ..., ge=10.0, le=200.0, description="Ekran mesafesi (cm)"
    )
    blinks_per_min: int = Field(
        ..., ge=0, le=60, description="Dakikadaki göz kırpma sayısı"
    )
    state: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Duruş durumu: 'good' | 'warning' | 'bad' | 'ok' | 'warn'",
    )


class IngestRequest(BaseModel):
    """Toplu metrik gönderim isteği."""

    session_id: str
    samples: list[MetricSample] = Field(..., min_length=1, max_length=500)


class IngestResponse(BaseModel):
    """Toplu metrik kabul yanıtı."""

    accepted: int
    session_id: str


class MetricSampleResponse(MetricSample):
    """Depolanmış metrik örneği yanıtı."""

    id: int
    session_id: str

    class Config:
        from_attributes = True


class MetricListResponse(BaseModel):
    """Metrik listesi yanıtı."""

    samples: list[MetricSampleResponse]
    total: int


# ---------------------------------------------------------------------------
# Uç noktalar
# ---------------------------------------------------------------------------


@router.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Toplu metrik gönder",
    description=(
        "İstemciden sayısal ergonomi özetlerini toplu alır ve veritabanına yazar. "
        "Kamera karesi asla gönderilmez."
    ),
)
@router.post(
    "/",
    response_model=IngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    include_in_schema=False,
)
def ingest(
    body: IngestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IngestResponse:
    """Bir oturuma ait toplu metrik örneklerini kabul eder."""
    service = MetricsService(
        metric_repo=MetricRepository(db),
        session_repo=SessionRepository(db),
    )
    sample_dicts = [s.model_dump() for s in body.samples]
    accepted = service.ingest(
        session_id=body.session_id,
        user_id=current_user.id,
        samples=sample_dicts,
    )
    return IngestResponse(accepted=accepted, session_id=body.session_id)


@router.get(
    "/",
    response_model=MetricListResponse,
    summary="Metrik örnekleri listele",
    description="Belirtilen oturum veya tarih aralığındaki metrik örneklerini döner.",
)
def list_metrics(
    session_id: str = Query(..., description="Oturum ID'si"),
    start: datetime | None = Query(
        None, description="Başlangıç zamanı (UTC, ISO 8601)"
    ),
    end: datetime | None = Query(None, description="Bitiş zamanı (UTC, ISO 8601)"),
    limit: int = Query(100, ge=1, le=1000, description="Sayfa başı kayıt sayısı"),
    offset: int = Query(0, ge=0, description="Atlama sayısı"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MetricListResponse:
    """Zaman dilimi ve oturum filtresiyle metrik örneklerini döner."""
    service = MetricsService(
        metric_repo=MetricRepository(db),
        session_repo=SessionRepository(db),
    )
    samples, total = service.get_metrics(
        session_id=session_id,
        user_id=current_user.id,
        from_ts=start,
        to_ts=end,
        limit=limit,
        offset=offset,
    )
    return MetricListResponse(
        samples=[
            MetricSampleResponse(
                id=s.id,
                session_id=str(s.session_id),
                ts=s.ts,
                neck_ratio=s.neck_ratio,
                shoulder_tilt=s.shoulder_tilt,
                distance_cm=s.distance_cm,
                blinks_per_min=s.blinks_per_min,
                state=s.state,
            )
            for s in samples
        ],
        total=total,
    )
