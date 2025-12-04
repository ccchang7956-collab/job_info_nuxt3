from fastapi import APIRouter, Request, Query, Depends
from sqlalchemy import text, select, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db
from app.models.models import JobDataUpdateLog
from fastapi.responses import JSONResponse
import math

router = APIRouter()

@router.get("/logs", response_class=JSONResponse)
async def get_logs(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    action: str = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    # Calculate offset
    offset = (page - 1) * per_page

    # Build query
    query = select(JobDataUpdateLog).order_by(JobDataUpdateLog.start_time.desc())

    if action:
        query = query.where(JobDataUpdateLog.action == action)

    # Execute query with pagination
    # Note: SQLAlchemy's async pagination is a bit manual
    
    # Get total count first
    count_query = select(text("COUNT(*)")).select_from(JobDataUpdateLog)
    if action:
        count_query = count_query.where(JobDataUpdateLog.action == action)
    
    total_count_result = await db.execute(count_query)
    total_count = total_count_result.scalar()

    # Get paginated results
    result = await db.execute(query.limit(per_page).offset(offset))
    logs = result.scalars().all()

    # Get distinct actions for filter
    actions_result = await db.execute(select(distinct(JobDataUpdateLog.action)))
    actions = actions_result.scalars().all()

    # Calculate total pages
    total_pages = math.ceil(total_count / per_page) if total_count else 0
    
    # Generate page range (simple version)
    page_range_start = max(1, page - 2)
    page_range_end = min(total_pages, page + 2)
    page_range = list(range(page_range_start, page_range_end + 1))

    return {
        "logs": [
            {
                "id": log.id,
                "action": log.action,
                "start_time": log.start_time.strftime("%Y-%m-%d %H:%M:%S") if log.start_time else None,
                "end_time": log.end_time.strftime("%Y-%m-%d %H:%M:%S") if log.end_time else None,
                "new_records": log.new_records,
                "updated_records": log.updated_records,
                "status": log.status,
                "remarks": log.remarks
            } for log in logs
        ],
        "actions": actions,
        "current_page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "total_count": total_count,
        "page_range": page_range
    }
