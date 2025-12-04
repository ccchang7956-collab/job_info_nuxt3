from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.Core.Database import get_async_db
from app.Services.LogService import LogService

router = APIRouter()

@router.get("/logs", response_class=JSONResponse)
@router.get("/log", response_class=JSONResponse)
async def get_logs(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    action: str = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    return await LogService.get_logs(db, page, per_page, action)
