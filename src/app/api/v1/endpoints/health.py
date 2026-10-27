"""Health check endpoint router."""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.health import HealthCheckResponse

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def check_health() -> HealthCheckResponse:
    """Check service health and return status metadata."""
    return HealthCheckResponse(
        status="healthy",
        app_name=settings.app_name,
        environment=settings.app_env,
    )
