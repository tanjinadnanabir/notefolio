import uuid
import math

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.note import (
    NoteCreate,
    NoteResponse,
    NoteListResponse,
    NoteUpdate,
    TrashNoteResponse,
)
from app.services.note import (
    create_note,
    get_deleted_note,
    get_note,
    list_notes,
    list_trash,
    permanently_delete_note,
    restore_note,
    update_note,
    delete_note,
)


router = APIRouter(
    prefix="/notes",
    tags=["Notes"],
)


# @router.post(
#     "",
#     response_model=NoteResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# def create_new_note(
#     note_data: NoteCreate,
#     current_user: User = Depends(
#         get_current_user
#     ),
#     db: Session = Depends(get_db),
# ):
#     return create_note(
#         db,
#         current_user.id,
#         note_data,
#     )


@router.post(
    "",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_note(
    note_data: NoteCreate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    try:
        return create_note(
            db,
            current_user.id,
            note_data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    

@router.get(
    "",
    response_model=NoteListResponse,
)
def get_notes(
    page: int = 1,
    page_size: int = 20,
    archived: bool | None = None,
    favorite: bool | None = None,
    pinned: bool | None = None,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    if page < 1:
        page = 1

    if page_size < 1:
        page_size = 20

    page_size = min(
        page_size,
        100,
    )

    notes, total = list_notes(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        archived=archived,
        favorite=favorite,
        pinned=pinned,
    )

    pages = math.ceil(
        total / page_size
    ) if total else 0

    return NoteListResponse(
        items=notes,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
    
    
@router.get(
    "/trash",
    response_model=list[TrashNoteResponse],
)
def get_trash(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    return list_trash(
        db,
        current_user.id,
    )
    
    
@router.get(
    "/{note_id}",
    response_model=NoteResponse,
)
def get_single_note(
    note_id: uuid.UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    note = get_note(
        db,
        note_id,
        current_user.id,
    )

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found.",
        )

    return note


@router.patch(
    "/{note_id}",
    response_model=NoteResponse,
)
def update_existing_note(
    note_id: uuid.UUID,
    note_data: NoteUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    note = get_note(
        db,
        note_id,
        current_user.id,
    )

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found.",
        )

    return update_note(
        db,
        note,
        note_data,
    )
    
    
@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_existing_note(
    note_id: uuid.UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    note = get_note(
        db,
        note_id,
        current_user.id,
    )

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found.",
        )

    delete_note(
        db,
        note,
    )

    return None


@router.post(
    "/{note_id}/restore",
    response_model=NoteResponse,
)
def restore_deleted_note(
    note_id: uuid.UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    note = get_deleted_note(
        db,
        note_id,
        current_user.id,
    )

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deleted note not found.",
        )

    return restore_note(
        db,
        note,
    )
    
    
@router.delete(
    "/{note_id}/permanent",
    status_code=status.HTTP_204_NO_CONTENT,
)
def permanently_delete_existing_note(
    note_id: uuid.UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    note = get_deleted_note(
        db,
        note_id,
        current_user.id,
    )

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deleted note not found.",
        )

    permanently_delete_note(
        db,
        note,
    )

    return None