"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.v1.router import api_v1_router
from app.core.body_limit import BodyLimitMiddleware
from app.core.config import settings
from app.core.database import engine
from app.core.errors import validation_error_handler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Manage application startup and shutdown lifecycle."""
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_middleware(BodyLimitMiddleware, max_bytes=settings.max_request_body_bytes)
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Root endpoint returning welcome message."""
    return {"message": f"Welcome to {settings.app_name} API"}
