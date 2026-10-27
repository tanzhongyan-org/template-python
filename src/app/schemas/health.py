"""Health domain schemas."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(default="healthy", description="Application status")
    app_name: str = Field(description="Name of the application")
    environment: str = Field(description="Active runtime environment")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp of the check",
    )
