"""API v1 router definition."""

from fastapi import APIRouter

from app.api.v1.endpoints import health

api_v1_router = APIRouter()
api_v1_router.include_router(health.router, tags=["Health"])

router = api_v1_router
