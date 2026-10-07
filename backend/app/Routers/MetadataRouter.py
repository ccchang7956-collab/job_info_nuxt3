from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from cachetools import TTLCache
from app.Core.Database import get_async_db
from app.Services.SeoService import PLACES
from app.Utils.DateUtils import get_latest_update_date

router = APIRouter()
category_cache = TTLCache(maxsize=1, ttl=300)


@router.get("/categories")
async def get_categories(response: Response, db: AsyncSession = Depends(get_async_db)):
    # Include the complete category table and historical announcements, not only
    # popular sitemap categories or categories that currently have open jobs.
    if "categories" not in category_cache:
        result = await db.execute(text("""
            SELECT sysnam FROM job_sysnam
            UNION SELECT sysnam FROM job_all_data
        """))
        sysnams = sorted({row[0].strip() for row in result
                          if row[0] and row[0].strip() not in ("無", "-")})
        category_cache["categories"] = {"places": PLACES, "sysnams": sysnams}
    response.headers["Cache-Control"] = "public, max-age=300"
    return category_cache["categories"]

@router.get("/last-update")
async def get_last_update():
    date = await get_latest_update_date()
    return {"date": date}
