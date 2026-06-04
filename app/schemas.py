from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# --- User Schemas ---

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    id: str
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Auth Schemas ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# --- Note Schemas ---

class NoteCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: str = Field(min_length=1, max_length=10000)

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, min_length=1, max_length=10000)

class NoteResponse(BaseModel):
    id: str
    title: Optional[str]
    content: str
    created_at: datetime
    updated_at: datetime
    owner_id: str

    model_config = {"from_attributes": True}

class NoteListResponse(BaseModel):
    total: int
    notes: list[NoteResponse]