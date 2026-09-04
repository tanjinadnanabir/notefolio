from pydantic import BaseModel

from app.schemas.note import NoteResponse


class SearchResponse(BaseModel):
    items: list[NoteResponse]
    query: str
    total: int