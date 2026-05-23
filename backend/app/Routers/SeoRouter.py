from fastapi import APIRouter, Response, Request, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.Core.Database import get_async_db
from app.Services.SeoService import SeoService

router = APIRouter()

@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    return SeoService.get_robots_txt()

@router.head("/robots.txt")
async def robots_txt_head():
    return Response(status_code=200, media_type="text/plain")

@router.get("/sitemap.xml", response_class=Response)
async def sitemap_xml(request: Request, db: AsyncSession = Depends(get_async_db)):
    content = await SeoService.get_sitemap_xml(db)
    return Response(content=content, media_type="application/xml")

@router.head("/sitemap.xml")
async def sitemap_xml_head():
    return Response(status_code=200, media_type="application/xml")
