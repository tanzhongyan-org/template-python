"""Note validation and DTO schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import StorableText


class NoteBase(BaseModel):
    """Base fields for Note."""

    title: StorableText = Field(..., min_length=1, max_length=200, description="Title of the note")
    body: StorableText = Field(default="", description="Body content of the note")


class NoteCreate(NoteBase):
    """Payload to create a new note."""

    pass


class NoteUpdate(BaseModel):
    """Payload to update an existing note."""

    title: StorableText | None = Field(
        default=None, min_length=1, max_length=200, description="Updated title"
    )
    body: StorableText | None = Field(default=None, description="Updated body content")


class NoteResponse(NoteBase):
    """Note entity response schema."""

    id: int
    owner_id: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
