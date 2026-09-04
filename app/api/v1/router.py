from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.notes import router as notes_router
from app.api.v1.folders import router as folders_router
from app.api.v1.tags import router as tags_router
from app.api.v1.search import router as search_router

api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(auth_router)
api_router.include_router(notes_router)
api_router.include_router(folders_router)
api_router.include_router(tags_router)
api_router.include_router(search_router)
