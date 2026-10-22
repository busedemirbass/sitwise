"""
API v1 ana router — tüm kaynak router'larını /api/v1 altında toplar.
SW-015: OpenAPI spesifikasyonu v1
"""

from fastapi import APIRouter

from api.v1.routers import (
    alerts,
    auth,
    calibration,
    metrics,
    sessions,
    summaries,
    thresholds,
)

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth.router)
api_v1_router.include_router(sessions.router)
api_v1_router.include_router(metrics.router)
api_v1_router.include_router(alerts.router)
api_v1_router.include_router(summaries.router)
api_v1_router.include_router(calibration.router)
api_v1_router.include_router(thresholds.router)
