import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.note import Note


def search_notes(
    db: Session,
    user_id: uuid.UUID,
    query: str,
) -> list[Note]:

    search_query = func.plainto_tsquery(
        "english",
        query,
    )

    statement = (
        select(Note)
        .where(
            Note.user_id == user_id,
            Note.deleted_at.is_(None),
            Note.search_vector.op("@@")(
                search_query
            ),
        )
        .order_by(
            func.ts_rank(
                Note.search_vector,
                search_query,
            ).desc(),
            Note.updated_at.desc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )