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
from app.models.folder import Folder
from app.models.user import User
from app.schemas.folder import (
    FolderCreate,
    FolderResponse,
    FolderUpdate,
)
from app.services.folder import (
    create_folder,
    delete_folder,
    get_folder,
    update_folder,
)


router = APIRouter(
    prefix="/folders",
    tags=["Folders"],
)


@router.post(
    "",
    response_model=FolderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_folder(
    folder_data: FolderCreate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    try:
        return create_folder(
            db,
            current_user.id,
            folder_data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
        

@router.get(
    "",
    response_model=list[FolderResponse],
)
def list_folders(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    statement = (
        select(Folder)
        .where(
            Folder.user_id == current_user.id
        )
        .order_by(
            Folder.name.asc()
        )
    )

    return list(
        db.scalars(statement).all()
    )
    
    
@router.get(
    "/{folder_id}",
    response_model=FolderResponse,
)
def get_single_folder(
    folder_id: uuid.UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    folder = get_folder(
        db,
        folder_id,
        current_user.id,
    )

    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found.",
        )

    return folder


@router.patch(
    "/{folder_id}",
    response_model=FolderResponse,
)
def update_existing_folder(
    folder_id: uuid.UUID,
    folder_data: FolderUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    folder = get_folder(
        db,
        folder_id,
        current_user.id,
    )

    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found.",
        )

    try:
        return update_folder(
            db,
            folder,
            folder_data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
        
        
def is_descendant(
    db: Session,
    folder_id: uuid.UUID,
    possible_parent_id: uuid.UUID,
) -> bool:

    current = get_folder(
        db,
        possible_parent_id,
        # This function will only be called
        # after ownership has been validated.
        # We need the folder owner here.
        # A simpler implementation follows below.
        folder_id,
    )
    
    
@router.delete(
    "/{folder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_existing_folder(
    folder_id: uuid.UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    folder = get_folder(
        db,
        folder_id,
        current_user.id,
    )

    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found.",
        )

    delete_folder(
        db,
        folder,
    )

    return None