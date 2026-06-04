from fastapi import APIRouter, Request, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.Core.Database import get_async_db
from app.Services.JobService import JobService

from app.Schemas.Schemas import JobDetailResponse

router = APIRouter()

@router.get("/Active_job_openings/{job_id}", response_model=JobDetailResponse)
async def get_job_details(
    request: Request, 
    job_id: int, 
    from_url: str = None, 
    include_parttime: bool = Query(False), 
    db: AsyncSession = Depends(get_async_db)
):
    result = await JobService.get_job_detail(db, job_id, from_url)
    
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
        
    response = JSONResponse(content=result)
    # 使用 max_age（秒數）取代 expires 字串，避免時區與格式問題
    response.set_cookie(key=f"job_viewed_{job_id}", value="1", max_age=3600, httponly=True, samesite="lax")
    return response
