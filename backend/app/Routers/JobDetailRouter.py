from fastapi import APIRouter, Request, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.Core.Database import get_async_db
from app.Services.JobService import JobService
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/Active_job_openings/{job_id}")
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
    expire_time = (datetime.now() + timedelta(hours=1)).strftime("%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key=f"job_viewed_{job_id}", value="1", expires=expire_time)
    return response
