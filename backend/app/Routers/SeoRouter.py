from fastapi import APIRouter, Response, Request, Depends
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.Core.Database import get_async_db
from app.Services.SeoService import SeoService

router = APIRouter()


# ── robots.txt ────────────────────────────────────────────────────────────────

@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    return SeoService.get_robots_txt()


@router.head("/robots.txt")
async def robots_txt_head():
    return Response(status_code=200, media_type="text/plain")


# ── Sitemap Index (根入口) ────────────────────────────────────────────────────

@router.get("/sitemap.xml", response_class=Response)
async def sitemap_index(request: Request, db: AsyncSession = Depends(get_async_db)):
    """Sitemap Index：列出所有子 sitemap，讓 Googlebot 依分頁爬取。"""
    # 先確保分頁快取存在（觸發一次職缺計數）
    await SeoService.get_sitemap_jobs_page(db, 1)
    content = await SeoService.get_sitemap_index()
    return Response(content=content, media_type="application/xml")


@router.head("/sitemap.xml")
async def sitemap_index_head():
    return Response(status_code=200, media_type="application/xml")


# ── 靜態頁面 Sitemap ──────────────────────────────────────────────────────────

@router.get("/sitemap-static.xml", response_class=Response)
async def sitemap_static():
    """靜態頁面 Sitemap（首頁、留言、圖表、關於、隱私權政策）。"""
    content = await SeoService.get_sitemap_static()
    return Response(content=content, media_type="application/xml")


@router.head("/sitemap-static.xml")
async def sitemap_static_head():
    return Response(status_code=200, media_type="application/xml")


# ── 職缺 Sitemap 分頁 ─────────────────────────────────────────────────────────

@router.get("/sitemap-jobs-{page}.xml", response_class=Response)
async def sitemap_jobs_page(page: int, db: AsyncSession = Depends(get_async_db)):
    """職缺 Sitemap 分頁，每頁最多 1000 筆 URL。"""
    if page < 1:
        return Response(status_code=400, content="Invalid page number")

    content = await SeoService.get_sitemap_jobs_page(db, page)
    if content is None:
        return Response(status_code=404, content="Page not found")

    return Response(content=content, media_type="application/xml")


@router.head("/sitemap-jobs-{page}.xml")
async def sitemap_jobs_page_head(page: int):
    return Response(status_code=200, media_type="application/xml")


# ── SEO 健康檢查 ──────────────────────────────────────────────────────────────

@router.get("/api/seo/health")
async def seo_health(request: Request):
    """SEO 基礎設施健康檢查：驗證 sitemap、robots.txt 可存取性。"""
    http_client = request.app.state.http_client
    result = await SeoService.get_seo_health(http_client)
    status_code = 200 if result["status"] == "healthy" else 503
    return JSONResponse(content=result, status_code=status_code)


# ── IndexNow 快取失效（供排程呼叫） ──────────────────────────────────────────

@router.post("/api/seo/invalidate-cache")
async def invalidate_seo_cache():
    """清除 sitemap 快取，通常在新職缺入庫後由排程呼叫。"""
    SeoService.invalidate_sitemap_cache()
    return {"message": "Sitemap cache invalidated successfully"}
