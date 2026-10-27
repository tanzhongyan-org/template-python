"""Schema types shared across features."""

from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field


class ErrorResponse(BaseModel):
    """Error body returned by every endpoint."""

    detail: str


def _reject_unstorable(value: str) -> str:
    """Reject text that Postgres cannot store: NUL bytes and lone surrogates."""
    if "\x00" in value:
        raise ValueError("must not contain NUL characters")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("must be valid Unicode text") from exc
    return value


StorableText = Annotated[str, AfterValidator(_reject_unstorable)]

# Primary keys are 32-bit integers; larger path IDs can never match a row.
RowId = Annotated[int, Field(ge=1, le=2_147_483_647)]
