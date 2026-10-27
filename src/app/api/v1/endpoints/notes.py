"""Notes API endpoints with owner isolation.

TEMPLATE-TODO(example): replace the notes slice with your first real feature
"""

from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy import desc, select

from app.core.auth import OwnerId
from app.core.database import DbSession
from app.models.note import Note
from app.schemas.common import ErrorResponse, RowId
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate

router = APIRouter(
    responses={
        400: {"model": ErrorResponse, "description": "Malformed request body"},
        401: {"model": ErrorResponse, "description": "Missing or untrusted identity"},
        413: {"model": ErrorResponse, "description": "Request body too large"},
    }
)

NOTE_NOT_FOUND: dict[int | str, dict[str, Any]] = {
    404: {"model": ErrorResponse, "description": "Note not found"}
}
NoteId = Annotated[RowId, Path()]


async def get_owned_note(db: DbSession, note_id: int, owner_id: str) -> Note:
    """Return the note if it belongs to the owner, otherwise raise 404."""
    stmt = select(Note).where(Note.id == note_id, Note.owner_id == owner_id)
    note = (await db.execute(stmt)).scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(payload: NoteCreate, owner_id: OwnerId, db: DbSession) -> Note:
    """Create a new note for the authenticated owner."""
    note = Note(owner_id=owner_id, title=payload.title, body=payload.body)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@router.get("/", response_model=list[NoteResponse])
async def list_notes(owner_id: OwnerId, db: DbSession) -> list[Note]:
    """List all notes belonging to the authenticated owner."""
    stmt = select(Note).where(Note.owner_id == owner_id).order_by(desc(Note.created_at))
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{note_id}", response_model=NoteResponse, responses=NOTE_NOT_FOUND)
async def get_note(note_id: NoteId, owner_id: OwnerId, db: DbSession) -> Note:
    """Get a note by ID belonging to the authenticated owner."""
    return await get_owned_note(db, note_id, owner_id)


@router.patch("/{note_id}", response_model=NoteResponse, responses=NOTE_NOT_FOUND)
async def update_note(
    note_id: NoteId, payload: NoteUpdate, owner_id: OwnerId, db: DbSession
) -> Note:
    """Update a note by ID belonging to the authenticated owner."""
    note = await get_owned_note(db, note_id, owner_id)
    if payload.title is not None:
        note.title = payload.title
    if payload.body is not None:
        note.body = payload.body
    await db.commit()
    await db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOTE_NOT_FOUND)
async def delete_note(note_id: NoteId, owner_id: OwnerId, db: DbSession) -> None:
    """Delete a note by ID belonging to the authenticated owner."""
    note = await get_owned_note(db, note_id, owner_id)
    await db.delete(note)
    await db.commit()
