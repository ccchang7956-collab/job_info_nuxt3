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
    def _format_lastmod(date_str: str | None) -> str:
        """將 announce_date 格式 (YYYYMMDD) 轉換成 ISO 8601 格式 (YYYY-MM-DD)"""
        if not date_str or len(date_str) != 8:
            return datetime.now().strftime('%Y-%m-%d')
        try:
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')

    @staticmethod
    async def get_sitemap_xml(db: AsyncSession) -> str:
        # Check cache first
        if "sitemap" in sitemap_cache:
            return sitemap_cache["sitemap"]

        base_url = SITE_DOMAIN
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        # 靜態路由設定（priority 和 changefreq）
        static_routes = [
            {"path": "/", "priority": "1.0", "changefreq": "daily"},
            {"path": "/comments", "priority": "0.7", "changefreq": "daily"},
            {"path": "/charts", "priority": "0.7", "changefreq": "daily"},
            {"path": "/about", "priority": "0.5", "changefreq": "monthly"},
            {"path": "/privacy-policy", "priority": "0.3", "changefreq": "yearly"},
        ]
        
        xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        
        # Add static routes
        for route in static_routes:
            xml_content.append('<url>')
            xml_content.append(f'<loc>{base_url}{route["path"]}</loc>')
            xml_content.append(f'<lastmod>{today_str}</lastmod>')
            xml_content.append(f'<changefreq>{route["changefreq"]}</changefreq>')
            xml_content.append(f'<priority>{route["priority"]}</priority>')
            xml_content.append('</url>')
            
        # Add dynamic job routes (Active jobs only)
        try:
            today = datetime.now()
            roc_year = today.year - 1911
            roc_today = f"{roc_year}{today.strftime('%m%d')}"
            
            stmt = (
                select(JobAllData.id, JobAllData.announce_date)
                .where(JobAllData.date_to >= roc_today)
                .order_by(desc(JobAllData.date_from))
                .limit(5000)
            )
            
            result = await db.execute(stmt)
            jobs = result.all()
            
            for row in jobs:
                job_id = row.id
                lastmod = SeoService._format_lastmod(row.announce_date)
                xml_content.append('<url>')
                xml_content.append(f'<loc>{base_url}/job/{job_id}</loc>')
                xml_content.append(f'<lastmod>{lastmod}</lastmod>')
                xml_content.append('<changefreq>weekly</changefreq>')
                xml_content.append('<priority>0.8</priority>')
                xml_content.append('</url>')
                
        except Exception as e:
            logging.error(f"Error generating sitemap: {e}")
            
        xml_content.append('</urlset>')
        
        final_content = "\n".join(xml_content)
        
        # Update cache
        sitemap_cache["sitemap"] = final_content
        
        return final_content
