from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.auth.dependencies import get_current_user
from app import schemas, crud, models

router = APIRouter(prefix="/notes", tags=["notes"])

@router.post("/", response_model=schemas.NoteResponse, status_code=201)
def create_note(
    note: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_note(db, note, current_user.id)


@router.get("/", response_model=schemas.NoteListResponse)
def list_notes(
    search: Optional[str] = Query(None, description="Search notes by title or content"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_notes(db, current_user.id, search=search)


@router.get("/{note_id}", response_model=schemas.NoteResponse)
def get_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    note = crud.get_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return note


@router.patch("/{note_id}", response_model=schemas.NoteResponse)
def update_note(
    note_id: str,
    note_data: schemas.NoteUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    note = crud.update_note(db, note_id, note_data, current_user.id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return note


@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    note = crud.delete_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )