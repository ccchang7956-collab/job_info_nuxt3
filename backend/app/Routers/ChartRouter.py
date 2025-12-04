from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.Core.Database import get_async_db
from app.Services.ChartService import ChartService

router = APIRouter()

@router.get("/job_openings_chart", response_class=JSONResponse)
async def get_job_openings_chart(request: Request, month: str = Query(None, regex=r"^\d{5,6}$"), db: AsyncSession = Depends(get_async_db)):
    try:
        return await ChartService.get_top_orgs(db, month)
    except Exception as e:
        # Log the error but do not expose traceback to the client
        print(f"Error in get_job_openings_chart: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

@router.get("/job_openings_chart_by_sysnam", response_class=JSONResponse)
async def get_job_openings_sysnam_chart(request: Request, month: str = Query(None, regex=r"^\d{5,6}$"), db: AsyncSession = Depends(get_async_db)):
    return await ChartService.get_top_sysnams(db, month)

@router.get("/job_openings_daily_chart", response_class=JSONResponse)
async def get_job_openings_daily_chart(request: Request, month: str = Query(None, regex=r"^\d{5,6}$"), db: AsyncSession = Depends(get_async_db)):
    return await ChartService.get_daily_job_counts(db, month)

@router.get("/job_openings_workplace_chart", response_class=JSONResponse)
async def get_job_openings_workplace_chart(request: Request, month: str = Query(None, regex=r"^\d{5,6}$"), db: AsyncSession = Depends(get_async_db)):
    return await ChartService.get_workplace_counts(db, month)

@router.get("/job_openings_commentscount_chart", response_class=JSONResponse)
async def job_openings_commentscount_chart(request: Request, db: AsyncSession = Depends(get_async_db)):
    return await ChartService.get_most_commented_jobs(db)
