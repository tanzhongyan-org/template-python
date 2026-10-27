"""Health domain service."""

from app.core.config import settings
from app.domain.health.schemas import HealthCheckResponse


class HealthService:
    """Service providing application health status."""

    @staticmethod
    def get_health() -> HealthCheckResponse:
        """Return application health metadata."""
        return HealthCheckResponse(
            status="healthy",
            app_name=settings.app_name,
            environment=settings.app_env,
        )
