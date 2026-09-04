from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.search import SearchResponse
from app.services.search import search_notes


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get(
    "",
    response_model=SearchResponse,
)
def search(
    q: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    query = q.strip()

    if not query:
        return SearchResponse(
            items=[],
            query="",
            total=0,
        )

    notes = search_notes(
        db,
        current_user.id,
        query,
    )

    return SearchResponse(
        items=notes,
        query=query,
        total=len(notes),
    )