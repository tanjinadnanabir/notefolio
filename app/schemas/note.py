import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    content: str = Field(
        default="",
        max_length=100_000,
    )

    folder_id: uuid.UUID | None = None

    color: str | None = Field(
        default=None,
        max_length=30,
    )


class NoteUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    content: str | None = Field(
        default=None,
        max_length=100_000,
    )

    folder_id: uuid.UUID | None = None

    is_pinned: bool | None = None

    is_archived: bool | None = None

    is_favorite: bool | None = None

    color: str | None = Field(
        default=None,
        max_length=30,
    )


class NoteResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    folder_id: uuid.UUID | None

    title: str
    content: str
    excerpt: str | None

    is_pinned: bool
    is_archived: bool
    is_favorite: bool

    color: str | None
    status: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
    
    
class NoteListResponse(BaseModel):
    items: list[NoteResponse]
    total: int
    page: int
    page_size: int
    pages: int
    
    
class TrashNoteResponse(NoteResponse):
    deleted_at: datetime