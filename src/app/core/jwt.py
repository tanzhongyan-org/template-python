"""JWT validation against the product's JWKS.

Production callers send `Authorization: Bearer <token>` with a token issued by
the product's Better Auth `jwt` plugin. The signature is checked against the
JWKS document, plus issuer, audience and expiry. Every failure is a 401 with no
details. While `JWKS_URL`, `JWT_ISSUER` or `JWT_AUDIENCE` is unset, bearer
tokens are rejected and only the dev identity shortcut works.

TEMPLATE-TODO(auth): confirm the signer algorithms and the subject claim mapping.
"""

from typing import Any

import jwt
from fastapi import HTTPException, status

from app.core.config import settings

_JWKS_TIMEOUT_SECONDS = 5
_SIGNING_ALGORITHMS = ["RS256", "ES256"]

_client: jwt.PyJWKClient | None = None
_client_url: str | None = None


def _get_client() -> jwt.PyJWKClient | None:
    """Return the cached JWKS client, or None when JWT auth is unconfigured."""
    global _client, _client_url
    url = settings.jwks_url
    if not url or not settings.jwt_issuer or not settings.jwt_audience:
        return None
    if _client is None or _client_url != url:
        _client = jwt.PyJWKClient(url, cache_keys=True, timeout=_JWKS_TIMEOUT_SECONDS)
        _client_url = url
    return _client


def validate_token(token: str) -> dict[str, Any]:
    """Verify a bearer token and return its claims, or raise 401."""
    client = _get_client()
    if client is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    try:
        key = client.get_signing_key_from_jwt(token).key
        claims: dict[str, Any] = jwt.decode(
            token,
            key,
            algorithms=_SIGNING_ALGORITHMS,
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"require": ["exp"]},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        ) from None
    return claims


def token_owner_id(token: str) -> str:
    """Return the owner id (`sub`) for a bearer token, or raise 401."""
    subject = validate_token(token).get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return subject
