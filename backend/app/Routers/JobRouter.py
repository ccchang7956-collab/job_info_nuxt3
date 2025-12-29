from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.Core.Database import get_async_db
from app.Services.JobService import JobService
from typing import Optional

from app.Schemas.Schemas import JobListResponse

router = APIRouter()

@router.get("/", response_model=JobListResponse)
async def get_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(15, ge=1, le=100),
    org: str = Query(None),
    title: str = Query(None),
    sysnam: str = Query(None),
    places: str = Query(None),
    min_rank: Optional[str] = Query(None),
    max_rank: Optional[str] = Query(None),
    include_history: bool = Query(False),
    include_parttime: bool = Query(False),
    sort: str = Query("date_from"),
    order: str = Query("desc"),
    db: AsyncSession = Depends(get_async_db)
):
    # Convert rank to int if possible
    try:
        min_rank_int = int(min_rank) if min_rank and min_rank.strip() != "" else None
    except ValueError:
        min_rank_int = None
    try:
        max_rank_int = int(max_rank) if max_rank and max_rank.strip() != "" else None
    except ValueError:
        max_rank_int = None

    return await JobService.get_jobs(
        db=db,
        page=page,
        per_page=per_page,
        org=org,
        title=title,
        sysnam=sysnam,
        places=places,
        min_rank=min_rank_int,
        max_rank=max_rank_int,
        include_history=include_history,
        include_parttime=include_parttime,
        sort=sort,
        order=order
    )
