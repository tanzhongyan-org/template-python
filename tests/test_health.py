"""Tests for health check endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint() -> None:
    """Verify root endpoint returns welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "template-python" in data["message"]


def test_health_check_endpoint() -> None:
    """Verify health check endpoint returns healthy status and metadata."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "template-python"
    assert data["environment"] == "development"
    assert "timestamp" in data
