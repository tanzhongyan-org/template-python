"""Health check endpoint router."""

from fastapi import APIRouter

from app.domain.health.schemas import HealthCheckResponse
from app.domain.health.service import HealthService

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthCheckResponse)
def check_health() -> HealthCheckResponse:
    """Check service health and status."""
    return HealthService.get_health()
