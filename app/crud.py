from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timezone
from typing import Optional
from app import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Password Utilities ---

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --- User CRUD ---

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed = hash_password(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- Note CRUD ---

def create_note(db: Session, note: schemas.NoteCreate, user_id: str):
    db_note = models.Note(
        title=note.title,
        content=note.content,
        owner_id=user_id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_notes(db: Session, user_id: str, search: Optional[str] = None):
    query = db.query(models.Note).filter(models.Note.owner_id == user_id)
    if search:
        query = query.filter(
            or_(
                models.Note.content.ilike(f"%{search}%"),
                models.Note.title.ilike(f"%{search}%")
            )
        )
    notes = query.order_by(models.Note.created_at.desc()).all()
    return {"total": len(notes), "notes": notes}

def get_note(db: Session, note_id: str, user_id: str):
    return db.query(models.Note).filter(
        models.Note.id == note_id,
        models.Note.owner_id == user_id
    ).first()

def delete_note(db: Session, note_id: str, user_id: str):
    db_note = get_note(db, note_id, user_id)
    if db_note:
        db.delete(db_note)
        db.commit()
    return db_note

def update_note(db: Session, note_id: str, note_data: schemas.NoteUpdate, user_id: str):
    db_note = get_note(db, note_id, user_id)
    if not db_note:
        return None
    if note_data.title is not None:
        db_note.title = note_data.title
    if note_data.content is not None:
        db_note.content = note_data.content
    db_note.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_note)
    return db_note