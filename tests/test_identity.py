"""Identity is fail-closed: no trusted header, no access."""

import pytest
from httpx import AsyncClient

from app.core.config import settings


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
