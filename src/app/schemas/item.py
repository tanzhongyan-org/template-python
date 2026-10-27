"""Item schemas for requests and responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    """Base schema for item attributes."""

    title: str = Field(..., max_length=255, description="Item title")
    description: str | None = Field(default=None, description="Detailed description")


class ItemCreate(ItemBase):
    """Schema for creating a new item."""

    pass


class ItemRead(ItemBase):
    """Schema for reading an item."""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
