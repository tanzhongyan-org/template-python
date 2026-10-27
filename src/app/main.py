"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.v1.router import api_v1_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/")
def root() -> dict[str, str]:
    """Root status endpoint."""
    return {"message": f"Welcome to {settings.app_name}"}
