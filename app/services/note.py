import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.note import Note
from app.models.tag import Tag

from app.schemas.note import NoteCreate, NoteUpdate

from app.services.folder import get_folder

def generate_excerpt(
    content: str,
    max_length: int = 200,
) -> str | None:

    text = " ".join(
        content.strip().split()
    )

    if not text:
        return None

    if len(text) <= max_length:
        return text

    return text[:max_length].rstrip() + "..."


# def create_note(
#     db: Session,
#     user_id: uuid.UUID,
#     note_data: NoteCreate,
# ) -> Note:

#     note = Note(
#         user_id=user_id,
#         folder_id=note_data.folder_id,
#         title=note_data.title,
#         content=note_data.content,
#         excerpt=generate_excerpt(
#             note_data.content
#         ),
#         color=note_data.color,
#     )

#     db.add(note)
#     db.commit()
#     db.refresh(note)

#     return note


def create_note(
    db: Session,
    user_id: uuid.UUID,
    note_data: NoteCreate,
) -> Note:

    if note_data.folder_id is not None:

        folder = get_folder(
            db,
            note_data.folder_id,
            user_id,
        )

        if folder is None:
            raise ValueError(
                "Folder not found."
            )

    note = Note(
        user_id=user_id,
        folder_id=note_data.folder_id,
        title=note_data.title,
        content=note_data.content,
        excerpt=generate_excerpt(
            note_data.content
        ),
        color=note_data.color,
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return note


def get_note(
    db: Session,
    note_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Note | None:

    statement = select(Note).where(
        Note.id == note_id,
        Note.user_id == user_id,
        Note.deleted_at.is_(None),
    )

    return db.scalar(statement)


def list_notes(
    db: Session,
    user_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
    archived: bool | None = None,
    favorite: bool | None = None,
    pinned: bool | None = None,
) -> tuple[list[Note], int]:

    filters = [
        Note.user_id == user_id,
        Note.deleted_at.is_(None),
    ]

    if archived is not None:
        filters.append(
            Note.is_archived == archived
        )

    if favorite is not None:
        filters.append(
            Note.is_favorite == favorite
        )

    if pinned is not None:
        filters.append(
            Note.is_pinned == pinned
        )

    count_statement = (
        select(func.count(Note.id))
        .where(*filters)
    )

    total = db.scalar(
        count_statement
    ) or 0

    statement = (
        select(Note)
        .where(*filters)
        .order_by(
            Note.is_pinned.desc(),
            Note.updated_at.desc(),
        )
        .offset(
            (page - 1) * page_size
        )
        .limit(page_size)
    )

    notes = list(
        db.scalars(statement).all()
    )

    return notes, total


def update_note(
    db: Session,
    note: Note,
    note_data: NoteUpdate,
) -> Note:

    update_data = note_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():

        if field == "content":
            note.excerpt = generate_excerpt(
                value
            )

        setattr(
            note,
            field,
            value,
        )

    db.commit()
    db.refresh(note)

    return note


def delete_note(
    db: Session,
    note: Note,
) -> None:

    note.deleted_at = datetime.now(
        timezone.utc
    )

    db.commit()
    
    
def list_trash(
    db: Session,
    user_id: uuid.UUID,
) -> list[Note]:

    statement = (
        select(Note)
        .where(
            Note.user_id == user_id,
            Note.deleted_at.is_not(None),
        )
        .order_by(
            Note.deleted_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )
    
    
def restore_note(
    db: Session,
    note: Note,
) -> Note:

    note.deleted_at = None

    db.commit()
    db.refresh(note)

    return note


def get_deleted_note(
    db: Session,
    note_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Note | None:

    statement = select(Note).where(
        Note.id == note_id,
        Note.user_id == user_id,
        Note.deleted_at.is_not(None),
    )

    return db.scalar(statement)


def permanently_delete_note(
    db: Session,
    note: Note,
) -> None:

    db.delete(note)
    db.commit()
    
    
def add_tag_to_note(
    db: Session,
    note: Note,
    tag: Tag,
) -> Note:

    if tag not in note.tags:
        note.tags.append(tag)

    db.commit()
    db.refresh(note)

    return note


def remove_tag_from_note(
    db: Session,
    note: Note,
    tag: Tag,
) -> Note:

    if tag in note.tags:
        note.tags.remove(tag)

    db.commit()
    db.refresh(note)

    return note