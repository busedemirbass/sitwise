"""
Metrics router — ergonomi metrik örneklerini toplu gönderme ve sorgulama uçları.
SW-015: OpenAPI spesifikasyonu v1

Kural: Kamera kareleri asla gönderilmez; yalnızca sayısal özetler iletilir.
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/metrics", tags=["Metrics"])


# ---------------------------------------------------------------------------
# Request / Response şemaları
# ---------------------------------------------------------------------------


class MetricSample(BaseModel):
    """Tek bir metrik örneği — istemcide hesaplanmış sayısal değerler."""

    ts: datetime = Field(..., description="Örnek zaman damgası (UTC)")
    neck_ratio: float = Field(..., ge=0.0, le=2.0, description="Boyun eğim oranı")
    shoulder_tilt: float = Field(..., ge=-90.0, le=90.0, description="Omuz eğimi (derece)")
    distance_cm: float = Field(..., ge=10.0, le=200.0, description="Ekran mesafesi (cm)")
    blinks_per_min: int = Field(..., ge=0, le=60, description="Dakikadaki göz kırpma sayısı")
    state: str = Field(..., description="Duruş durumu: 'good' | 'warning' | 'bad'")


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
def ingest(body: IngestRequest) -> IngestResponse:
    """Bir oturuma ait toplu metrik örneklerini kabul eder."""
    # TODO (SW-impl): MetricsService.ingest() çağrısı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")


@router.get(
    "/",
    response_model=MetricListResponse,
    summary="Metrik örnekleri listele",
    description="Belirtilen tarih aralığındaki metrik örneklerini döner.",
)
def list_metrics(
    session_id: str | None = Query(None, description="Filtre: oturum ID'si"),
    start: datetime | None = Query(None, description="Başlangıç zamanı (UTC, ISO 8601)"),
    end: datetime | None = Query(None, description="Bitiş zamanı (UTC, ISO 8601)"),
    limit: int = Query(100, ge=1, le=1000, description="Sayfa başı kayıt sayısı"),
    offset: int = Query(0, ge=0, description="Atlama sayısı"),
) -> MetricListResponse:
    """Zaman dilimi ve oturum filtresiyle metrik örneklerini döner."""
    # TODO (SW-impl): MetricRepository.by_date_range() çağrısı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")
