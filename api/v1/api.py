from fastapi import APIRouter
from app.api.v1.endpoints import candidates, cv_upload, search

api_router = APIRouter()

api_router.include_router(
    candidates.router,
    prefix="/candidates",
    tags=["candidates"]
)

api_router.include_router(
    cv_upload.router,
    prefix="/cv",
    tags=["cv"]
)

api_router.include_router(
    search.router,
    prefix="/search",
    tags=["search"]
) 