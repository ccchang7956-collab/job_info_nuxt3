from fastapi import APIRouter, Response, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy import text
from app.database import get_async_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

router = APIRouter()

from cachetools import TTLCache

# Cache sitemap for 1 hour (3600 seconds)
sitemap_cache = TTLCache(maxsize=1, ttl=3600)

@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    content = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /private/

Sitemap: https://www.opendgpa.site/sitemap.xml
"""
    return content

@router.get("/sitemap.xml", response_class=Response)
async def sitemap_xml(request: Request, db: AsyncSession = Depends(get_async_db)):
    # Check cache first
    if "sitemap" in sitemap_cache:
        return Response(content=sitemap_cache["sitemap"], media_type="application/xml")

    base_url = "https://www.opendgpa.site"
    
    # Static routes
    static_routes = [
        "/",
        "/Job_Comments",
        "/job_openings_chart",
        "/job_openings_chart_by_sysnam",
        "/job_openings_workplace_chart",
        "/job_openings_daily_chart",
        "/job_openings_commentscount_chart",
        "/line/intro",
        "/about",
        "/PrivacyPolicy",
    ]
    
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Add static routes
    for route in static_routes:
        xml_content.append('<url>')
        xml_content.append(f'<loc>{base_url}{route}</loc>')
        xml_content.append('<changefreq>daily</changefreq>')
        xml_content.append('<priority>0.8</priority>')
        xml_content.append('</url>')
        
    # Add dynamic job routes (Active jobs only to keep sitemap manageable and relevant)
    # We limit to recent 5000 active jobs to avoid timeout/memory issues
    try:
        query = text("""
            SELECT id, date_from 
            FROM job_all_data 
            WHERE date_to >= :today 
            ORDER BY date_from DESC 
            LIMIT 5000
        """)
        
        # Calculate today's ROC date for comparison
        today = datetime.now()
        roc_year = today.year - 1911
        roc_today = f"{roc_year}{today.strftime('%m%d')}"
        
        result = await db.execute(query, {"today": roc_today})
        jobs = result.fetchall()
        
        for job in jobs:
            xml_content.append('<url>')
            xml_content.append(f'<loc>{base_url}/Active_job_openings/{job.id}</loc>')
            xml_content.append('<changefreq>weekly</changefreq>')
            xml_content.append('<priority>0.6</priority>')
            xml_content.append('</url>')
            
    except Exception as e:
        print(f"Error generating sitemap: {e}")
        
    xml_content.append('</urlset>')
    
    final_content = "\n".join(xml_content)
    
    # Update cache
    sitemap_cache["sitemap"] = final_content
    
    return Response(content=final_content, media_type="application/xml")
