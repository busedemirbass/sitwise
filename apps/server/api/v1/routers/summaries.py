"""
Summaries router — günlük ve aralıklı özet rapor uçları.
SW-015: OpenAPI spesifikasyonu v1
"""

from datetime import date

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

router = APIRouter(prefix="/summaries", tags=["Summaries"])


# ---------------------------------------------------------------------------
# Request / Response şemaları
# ---------------------------------------------------------------------------


class DailySummaryResponse(BaseModel):
    """Günlük özet yanıtı."""

    id: str
    user_id: str
    date: date
    score: int
    good_minutes: int
    alert_count: int
    avg_blink: float


class SummaryRangeResponse(BaseModel):
    """Tarih aralığı özet listesi yanıtı."""

    summaries: list[DailySummaryResponse]
    total: int


# ---------------------------------------------------------------------------
# Uç noktalar
# ---------------------------------------------------------------------------


@router.get(
    "/daily",
    response_model=DailySummaryResponse,
    summary="Günlük özet",
    description="Belirtilen tarihe ait ergonomi özet puanını ve istatistiklerini döner.",
)
def daily_summary(
    target_date: date = Query(..., alias="date", description="Özet tarihi (YYYY-MM-DD)"),
) -> DailySummaryResponse:
    """Tek günlük ergonomi özetini döner."""
    # TODO (SW-impl): SummaryService.daily() çağrısı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")


@router.get(
    "/range",
    response_model=SummaryRangeResponse,
    summary="Tarih aralığı özeti",
    description="Belirtilen tarih aralığındaki günlük özetlerin listesini döner.",
)
def range_summary(
    start: date = Query(..., description="Başlangıç tarihi (YYYY-MM-DD)"),
    end: date = Query(..., description="Bitiş tarihi (YYYY-MM-DD)"),
) -> SummaryRangeResponse:
    """Tarih aralığındaki tüm günlük özetleri döner."""
    # TODO (SW-impl): SummaryService.range() çağrısı eklenecek
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Henüz uygulanmadı")
