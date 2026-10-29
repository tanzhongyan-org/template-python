"""Request identity."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.core.config import DEV_ENVS, settings
from app.core.jwt import token_owner_id


def dev_shortcut_enabled() -> bool:
    """True only when the dev identity shortcut may run.

    The shortcut needs both the explicit flag and a dev environment. Every
    other environment fails closed even when the flag is set.
    """
    return settings.trust_identity_header and settings.app_env in DEV_ENVS


def get_owner_id(
    x_user_id: Annotated[str | None, Header()] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    """Return the caller's owner ID, or reject the request with 401.

    A bearer token is validated against the product JWKS first. Without one,
    the `x-user-id` header is honoured only when the dev shortcut is enabled.
    A missing or blank identity never falls back to a shared value.

    TEMPLATE-TODO(auth): replace header identity with real authentication
    """
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() == "bearer" and token.strip():
            return token_owner_id(token.strip())
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    owner_id = x_user_id.strip() if x_user_id else ""
    if not dev_shortcut_enabled() or not owner_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return owner_id


OwnerId = Annotated[str, Depends(get_owner_id)]
