import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.schemas.tag import (
    TagCreate,
    TagUpdate,
)


def get_tag(
    db: Session,
    tag_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Tag | None:

    statement = select(Tag).where(
        Tag.id == tag_id,
        Tag.user_id == user_id,
    )

    return db.scalar(statement)

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.schemas.tag import (
    TagCreate,
    TagUpdate,
)


def get_tag(
    db: Session,
    tag_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Tag | None:

    statement = select(Tag).where(
        Tag.id == tag_id,
        Tag.user_id == user_id,
    )

    return db.scalar(statement)

def normalize_tag_name(
    name: str,
) -> str:

    return " ".join(
        name.strip().split()
    )
    
def create_tag(
    db: Session,
    user_id: uuid.UUID,
    tag_data: TagCreate,
) -> Tag:

    name = normalize_tag_name(
        tag_data.name
    )

    existing = db.scalar(
        select(Tag).where(
            Tag.user_id == user_id,
            Tag.name.ilike(name),
        )
    )

    if existing:
        raise ValueError(
            "Tag already exists."
        )

    tag = Tag(
        user_id=user_id,
        name=name,
        color=tag_data.color,
    )

    db.add(tag)
    db.commit()
    db.refresh(tag)

    return tag

def update_tag(
    db: Session,
    tag: Tag,
    tag_data: TagUpdate,
) -> Tag:

    data = tag_data.model_dump(
        exclude_unset=True
    )

    if "name" in data:

        name = normalize_tag_name(
            data["name"]
        )

        existing = db.scalar(
            select(Tag).where(
                Tag.user_id == tag.user_id,
                Tag.name.ilike(name),
                Tag.id != tag.id,
            )
        )

        if existing:
            raise ValueError(
                "Tag already exists."
            )

        data["name"] = name

    for field, value in data.items():
        setattr(
            tag,
            field,
            value,
        )

    db.commit()
    db.refresh(tag)

    return tag

def delete_tag(
    db: Session,
    tag: Tag,
) -> None:

    db.delete(tag)
    db.commit()