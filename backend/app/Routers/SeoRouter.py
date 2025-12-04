from fastapi import APIRouter, Response, Request, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.Core.Database import get_async_db
from app.Services.SeoService import SeoService

router = APIRouter()

@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    return SeoService.get_robots_txt()

@router.get("/sitemap.xml", response_class=Response)
async def sitemap_xml(request: Request, db: AsyncSession = Depends(get_async_db)):
    content = await SeoService.get_sitemap_xml(db)
    return Response(content=content, media_type="application/xml")
