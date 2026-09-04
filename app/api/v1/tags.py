import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.tag import Tag
from app.models.user import User
from app.schemas.tag import (
    TagCreate,
    TagResponse,
    TagUpdate,
)
from app.services.tag import (
    create_tag,
    delete_tag,
    get_tag,
    update_tag,
)


router = APIRouter(
    prefix="/tags",
    tags=["Tags"],
)


@router.post(
    "",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_tag(
    tag_data: TagCreate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    try:
        return create_tag(
            db,
            current_user.id,
            tag_data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
        

@router.get(
    "",
    response_model=list[TagResponse],
)
def list_tags(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    statement = (
        select(Tag)
        .where(
            Tag.user_id == current_user.id
        )
        .order_by(Tag.name.asc())
    )

    return list(
        db.scalars(statement).all()
    )
    
    
@router.get(
    "/{tag_id}",
    response_model=TagResponse,
)
def get_single_tag(
    tag_id: uuid.UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    tag = get_tag(
        db,
        tag_id,
        current_user.id,
    )

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found.",
        )

    return tag


@router.patch(
    "/{tag_id}",
    response_model=TagResponse,
)
def update_existing_tag(
    tag_id: uuid.UUID,
    tag_data: TagUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    tag = get_tag(
        db,
        tag_id,
        current_user.id,
    )

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found.",
        )

    try:
        return update_tag(
            db,
            tag,
            tag_data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
        
        
@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_existing_tag(
    tag_id: uuid.UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    tag = get_tag(
        db,
        tag_id,
        current_user.id,
    )

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found.",
        )

    delete_tag(
        db,
        tag,
    )

    return None