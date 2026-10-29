"""Identity is fail-closed: no trusted header, no access."""

import pytest
from httpx import AsyncClient
from pydantic import ValidationError

from app.core.auth import dev_shortcut_enabled
from app.core.config import Settings, settings


@pytest.mark.parametrize("headers", [{}, {"x-user-id": ""}, {"x-user-id": "   "}])
async def test_missing_or_blank_identity_returns_401(
    client: AsyncClient, headers: dict[str, str]
) -> None:
    response = await client.get("/api/v1/notes/", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


async def test_header_ignored_when_not_trusted(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "trust_identity_header", False)
    response = await client.post(
        "/api/v1/notes/",
        json={"title": "t", "body": "b"},
        headers={"x-user-id": "owner-1"},
    )
    assert response.status_code == 401


@pytest.mark.parametrize("app_env", ["production", "preview", "staging"])
def test_dev_flag_fails_boot_outside_dev(app_env: str) -> None:
    with pytest.raises(ValidationError):
        Settings(trust_identity_header=True, app_env=app_env)


@pytest.mark.parametrize("app_env", ["development", "test"])
def test_dev_flag_boots_in_dev(app_env: str) -> None:
    assert Settings(trust_identity_header=True, app_env=app_env)


@pytest.mark.parametrize(
    ("trust", "app_env", "expected"),
    [
        (True, "development", True),
        (True, "test", True),
        (True, "production", False),
        (True, "preview", False),
        (False, "development", False),
        (False, "test", False),
    ],
)
def test_dev_shortcut_guard_matrix(
    monkeypatch: pytest.MonkeyPatch, trust: bool, app_env: str, expected: bool
) -> None:
    monkeypatch.setattr(settings, "trust_identity_header", trust)
    monkeypatch.setattr(settings, "app_env", app_env)
    assert dev_shortcut_enabled() is expected


async def test_header_ignored_in_production(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "trust_identity_header", True)
    monkeypatch.setattr(settings, "app_env", "production")
    response = await client.get("/api/v1/notes/", headers={"x-user-id": "owner-1"})
    assert response.status_code == 401
