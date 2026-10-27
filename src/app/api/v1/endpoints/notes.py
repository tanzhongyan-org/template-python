"""Notes API endpoints with owner isolation."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate

router = APIRouter()


def get_owner_id(x_user_id: Annotated[str | None, Header()] = None) -> str:
    """Extract owner ID from request header with a stub fallback.

    Single swap point for real JWT/session authentication.
    """
    return x_user_id or "test-owner"


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    payload: NoteCreate,
    owner_id: Annotated[str, Depends(get_owner_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Note:
    """Create a new note for the authenticated owner."""
    note = Note(owner_id=owner_id, title=payload.title, body=payload.body)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@router.get("/", response_model=list[NoteResponse])
async def list_notes(
    owner_id: Annotated[str, Depends(get_owner_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Note]:
    """List all notes belonging to the authenticated owner."""
    stmt = select(Note).where(Note.owner_id == owner_id).order_by(desc(Note.created_at))
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    owner_id: Annotated[str, Depends(get_owner_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Note:
    """Get a note by ID belonging to the authenticated owner."""
    stmt = select(Note).where(and_(Note.id == note_id, Note.owner_id == owner_id))
    result = await db.execute(stmt)
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    return note


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    payload: NoteUpdate,
    owner_id: Annotated[str, Depends(get_owner_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Note:
    """Update a note by ID belonging to the authenticated owner."""
    stmt = select(Note).where(and_(Note.id == note_id, Note.owner_id == owner_id))
    result = await db.execute(stmt)
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    if payload.title is not None:
        note.title = payload.title
    if payload.body is not None:
        note.body = payload.body

    await db.commit()
    await db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    owner_id: Annotated[str, Depends(get_owner_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a note by ID belonging to the authenticated owner."""
    stmt = select(Note).where(and_(Note.id == note_id, Note.owner_id == owner_id))
    result = await db.execute(stmt)
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    await db.delete(note)
    await db.commit()
