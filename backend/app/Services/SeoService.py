from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from cachetools import TTLCache
from app.Models.Models import JobAllData
from app.Utils.FormatUtils import convert_to_gregorian_date
import logging
import os
from typing import Optional
from xml.sax.saxutils import escape

# Cache sitemap for 1 hour (3600 seconds)
sitemap_cache = TTLCache(maxsize=1, ttl=3600)

SITE_DOMAIN = os.getenv("SITE_DOMAIN", "https://opendgpa.shibaalin.com").rstrip("/")

class SeoService:
    @staticmethod
    def get_robots_txt() -> str:
        return f"""User-agent: *
Content-Signal: search=yes,ai-input=yes,ai-train=yes
Allow: /
Disallow: /admin/
Disallow: /logs

Sitemap: {SITE_DOMAIN}/sitemap.xml
LLMs: {SITE_DOMAIN}/llms.txt
LLMs-full: {SITE_DOMAIN}/llms-full.txt
"""

    @staticmethod
    def _format_lastmod(date_str: Optional[str]) -> str:
        """將民國日期 (YYYMMDD) 或西元日期 (YYYYMMDD) 轉成 ISO 8601 日期。"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')

        normalized = date_str.replace("/", "").replace("-", "")
        if len(normalized) == 7 and normalized.isdigit():
            converted = convert_to_gregorian_date(normalized)
            return converted or datetime.now().strftime('%Y-%m-%d')

        if len(normalized) == 8 and normalized.isdigit():
            return f"{normalized[:4]}-{normalized[4:6]}-{normalized[6:8]}"

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
            xml_content.append(f'<loc>{escape(base_url + route["path"])}</loc>')
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
                xml_content.append(f'<loc>{escape(f"{base_url}/job/{job_id}")}</loc>')
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
