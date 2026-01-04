from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from cachetools import TTLCache
from app.Models.Models import JobAllData
import logging
import os

# Cache sitemap for 1 hour (3600 seconds)
sitemap_cache = TTLCache(maxsize=1, ttl=3600)

# 從環境變數讀取網站網域
SITE_DOMAIN = os.getenv("SITE_DOMAIN", "https://nuxt3.opendgpa.site")

class SeoService:
    @staticmethod
    def get_robots_txt() -> str:
        return f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /logs

Sitemap: {SITE_DOMAIN}/sitemap.xml
"""

    @staticmethod
    async def get_sitemap_xml(db: AsyncSession) -> str:
        # Check cache first
        if "sitemap" in sitemap_cache:
            return sitemap_cache["sitemap"]

        base_url = SITE_DOMAIN
        
        # Static routes (使用新版路由)
        static_routes = [
            "/",
            "/comments",
            "/charts",
            "/about",
            "/privacy-policy",
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
            
        # Add dynamic job routes (Active jobs only)
        try:
            today = datetime.now()
            roc_year = today.year - 1911
            roc_today = f"{roc_year}{today.strftime('%m%d')}"
            
            stmt = (
                select(JobAllData.id)
                .where(JobAllData.date_to >= roc_today)
                .order_by(desc(JobAllData.date_from))
                .limit(5000)
            )
            
            result = await db.execute(stmt)
            jobs = result.scalars().all()
            
            for job_id in jobs:
                xml_content.append('<url>')
                xml_content.append(f'<loc>{base_url}/job/{job_id}</loc>')
                xml_content.append('<changefreq>weekly</changefreq>')
                xml_content.append('<priority>0.6</priority>')
                xml_content.append('</url>')
                
        except Exception as e:
            logging.error(f"Error generating sitemap: {e}")
            
        xml_content.append('</urlset>')
        
        final_content = "\n".join(xml_content)
        
        # Update cache
        sitemap_cache["sitemap"] = final_content
        
        return final_content
