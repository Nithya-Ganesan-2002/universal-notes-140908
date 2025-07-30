from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

# PUBLIC_INTERFACE
class UserRegisterRequest(BaseModel):
    """Request body for user registration."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")

# PUBLIC_INTERFACE
class UserLoginRequest(BaseModel):
    """Request body for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")

# PUBLIC_INTERFACE
class TokenResponse(BaseModel):
    """Token returned after authentication."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")

# PUBLIC_INTERFACE
class Tag(BaseModel):
    """A tag to organize notes."""
    id: Optional[str]
    name: str

# PUBLIC_INTERFACE
class Folder(BaseModel):
    """A folder to organize notes."""
    id: Optional[str]
    name: str

# PUBLIC_INTERFACE
class NoteBase(BaseModel):
    """Base fields for note creation/updating."""
    title: str = Field(..., description="Title of the note")
    content: str = Field(..., description="Note content")
    folder_id: Optional[str] = Field(None, description="ID of the folder the note belongs to")
    tags: Optional[List[str]] = Field(default_factory=list, description="List of tag IDs")

# PUBLIC_INTERFACE
class NoteCreate(NoteBase):
    """Schema for creating a note."""
    pass

# PUBLIC_INTERFACE
class NoteUpdate(NoteBase):
    """Schema for updating a note (all fields optional)."""
    title: Optional[str]
    content: Optional[str]
    folder_id: Optional[str]
    tags: Optional[List[str]]

# PUBLIC_INTERFACE
class Note(NoteBase):
    """A note including metadata."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class NotesList(BaseModel):
    """A list of notes."""
    notes: List[Note]
