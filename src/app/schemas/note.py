"""Note validation and DTO schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteBase(BaseModel):
    """Base fields for Note."""

    title: str = Field(..., min_length=1, max_length=200, description="Title of the note")
    body: str = Field(default="", description="Body content of the note")


class NoteCreate(NoteBase):
    """Payload to create a new note."""

    pass


class NoteUpdate(BaseModel):
    """Payload to update an existing note."""

    title: str | None = Field(
        default=None, min_length=1, max_length=200, description="Updated title"
    )
    body: str | None = Field(default=None, description="Updated body content")


class NoteResponse(NoteBase):
    """Note entity response schema."""

    id: int
    owner_id: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
