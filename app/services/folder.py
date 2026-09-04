import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.folder import Folder
from app.schemas.folder import (
    FolderCreate,
    FolderUpdate,
)


def get_folder(
    db: Session,
    folder_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Folder | None:

    statement = select(Folder).where(
        Folder.id == folder_id,
        Folder.user_id == user_id,
    )

    return db.scalar(statement)


def validate_parent_folder(
    db: Session,
    parent_id: uuid.UUID | None,
    user_id: uuid.UUID,
) -> Folder | None:

    if parent_id is None:
        return None

    parent = get_folder(
        db,
        parent_id,
        user_id,
    )

    if parent is None:
        raise ValueError(
            "Parent folder not found."
        )

    return parent


def create_folder(
    db: Session,
    user_id: uuid.UUID,
    folder_data: FolderCreate,
) -> Folder:

    validate_parent_folder(
        db,
        folder_data.parent_id,
        user_id,
    )

    folder = Folder(
        user_id=user_id,
        parent_id=folder_data.parent_id,
        name=folder_data.name,
        description=folder_data.description,
        color=folder_data.color,
    )

    db.add(folder)
    db.commit()
    db.refresh(folder)

    return folder


def update_folder(
    db: Session,
    folder: Folder,
    folder_data: FolderUpdate,
) -> Folder:

    data = folder_data.model_dump(
        exclude_unset=True
    )

    if "parent_id" in data:

        validate_parent_folder(
            db,
            data["parent_id"],
            folder.user_id,
        )

        if data["parent_id"] == folder.id:
            raise ValueError(
                "A folder cannot be its own parent."
            )

    for field, value in data.items():
        setattr(
            folder,
            field,
            value,
        )

    db.commit()
    db.refresh(folder)

    return folder


def delete_folder(
    db: Session,
    folder: Folder,
) -> None:

    for note in folder.notes:
        note.folder_id = None

    db.delete(folder)
    db.commit()