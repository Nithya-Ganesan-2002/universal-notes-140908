from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from .models import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    Note,
    NoteCreate,
    NoteUpdate,
    NotesList,
    Folder,
    Tag,
)
from .supabase_client import get_supabase_client, SupabaseClient

app = FastAPI(
    title="Notes API Backend",
    version="0.1.0",
    description="Backend REST API for universal notes app.",
    openapi_tags=[
        {"name": "Auth", "description": "User authentication APIs"},
        {"name": "Notes", "description": "CRUD operations for notes"},
        {"name": "Folders", "description": "Organize notes by folders"},
        {"name": "Tags", "description": "Organize notes by tags"},
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ------- AUTHENTICATION --------
@app.post("/auth/register", summary="Register", tags=["Auth"], response_model=TokenResponse)
def register(
    user: UserRegisterRequest,
    client: SupabaseClient = Depends(get_supabase_client)
):
    """
    Register a new user.
    - **email**: User email
    - **password**: User password
    Returns a JWT access token upon success.
    """
    result = client.register_user(user.email, user.password)
    # In actual implementation, issue token via Supabase after registration
    return {"access_token": result.get("id", "dummy"), "token_type": "bearer"}


@app.post("/auth/login", summary="Login", tags=["Auth"], response_model=TokenResponse)
def login(
    user: UserLoginRequest,
    client: SupabaseClient = Depends(get_supabase_client)
):
    """
    Login a user and return a token.
    - **email**: User email
    - **password**: User password
    """
    result = client.login_user(user.email, user.password)
    if not result or "access_token" not in result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return result

# Stub get_current_user dependency for now
def get_current_user(token: str = Depends(oauth2_scheme)):
    # In real setup, verify token with Supabase.
    # Here, we assume the token is user_id for example purposes.
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"user_id": token}

# ------- NOTES CRUD --------
@app.get("/notes", summary="List Notes", tags=["Notes"], response_model=NotesList)
def list_notes(
    folder_id: Optional[str] = None,
    tag_id: Optional[str] = None,
    search: Optional[str] = None,
    current_user=Depends(get_current_user),
    client: SupabaseClient = Depends(get_supabase_client),
):
    """
    List all notes for current user, with optional filtering.
    - **folder_id**: Filter by folder
    - **tag_id**: Filter by tag
    - **search**: Search in title/content
    """
    user_id = current_user["user_id"]
    notes = client.get_notes(user_id, folder_id=folder_id, tag_id=tag_id, search=search)
    notes_objs = [Note(**note) for note in notes]
    return {"notes": notes_objs}

@app.post("/notes", summary="Create Note", tags=["Notes"], response_model=Note)
def create_note(
    note: NoteCreate,
    current_user=Depends(get_current_user),
    client: SupabaseClient = Depends(get_supabase_client),
):
    """
    Create a new note for current user.
    """
    user_id = current_user["user_id"]
    created = client.create_note(user_id, note.dict())
    return Note(**created)

@app.put("/notes/{note_id}", summary="Update Note", tags=["Notes"], response_model=Note)
def update_note(
    note_id: str,
    note: NoteUpdate,
    current_user=Depends(get_current_user),
    client: SupabaseClient = Depends(get_supabase_client),
):
    """
    Update an existing note by note_id.
    """
    user_id = current_user["user_id"]
    updated = client.update_note(user_id, note_id, note.dict(exclude_unset=True))
    return Note(**updated)

@app.delete("/notes/{note_id}", summary="Delete Note", tags=["Notes"], response_model=dict)
def delete_note(
    note_id: str,
    current_user=Depends(get_current_user),
    client: SupabaseClient = Depends(get_supabase_client),
):
    """
    Delete a note by note_id.
    """
    user_id = current_user["user_id"]
    client.delete_note(user_id, note_id)
    return {"ok": True, "note_id": note_id}

@app.get("/notes/{note_id}", summary="Get Note", tags=["Notes"], response_model=Note)
def get_note(
    note_id: str,
    current_user=Depends(get_current_user),
    client: SupabaseClient = Depends(get_supabase_client),
):
    """
    Retrieve a single note by note_id.
    """
    user_id = current_user["user_id"]
    notes = client.get_notes(user_id)
    for n in notes:
        if n["id"] == note_id:
            return Note(**n)
    raise HTTPException(status_code=404, detail="Note not found")

# ------- FOLDERS AND TAGS --------
@app.get("/folders", summary="List Folders", tags=["Folders"], response_model=List[Folder])
def list_folders(
    current_user=Depends(get_current_user),
    client: SupabaseClient = Depends(get_supabase_client),
):
    """
    List all folders of the current user.
    """
    user_id = current_user["user_id"]
    return [Folder(**folder) for folder in client.get_folders(user_id)]

@app.get("/tags", summary="List Tags", tags=["Tags"], response_model=List[Tag])
def list_tags(
    current_user=Depends(get_current_user),
    client: SupabaseClient = Depends(get_supabase_client),
):
    """
    List all tags of the current user.
    """
    user_id = current_user["user_id"]
    return [Tag(**tag) for tag in client.get_tags(user_id)]

@app.get("/")
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}
