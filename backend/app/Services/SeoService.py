from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from cachetools import TTLCache
from app.Models.Models import JobAllData
from app.Utils.FormatUtils import convert_to_gregorian_date
import logging
import os
from typing import Optional
from xml.sax.saxutils import escape

# Cache sitemap for 30 minutes (1800 seconds)
# 縮短快cache，讓失效 URL 更快實際被清除，减少 Googlebot 抓到 404 的機率
sitemap_cache = TTLCache(maxsize=1, ttl=1800)

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
    def _format_lastmod(date_str=None, fallback_date_str=None) -> str:
        """將民國日期 (YYYMMDD) 或西元日期 (YYYYMMDD) 轉成 ISO 8601 日期。
        優先使用 date_str，若為空則嘗試 fallback_date_str，
        兩者都為空才回傳 None（由呼叫方決定要旧 fallback）。
        不再使用 datetime.now() 作為 fallback，
        避免 Google 誤以為每次都有新內容更新。"""
        for ds in [date_str, fallback_date_str]:
            if not ds:
                continue
            normalized = str(ds).replace("/", "").replace("-", "").strip()
            if len(normalized) == 7 and normalized.isdigit():
                converted = convert_to_gregorian_date(normalized)
                if converted:
                    return converted
            if len(normalized) == 8 and normalized.isdigit():
                return f"{normalized[:4]}-{normalized[4:6]}-{normalized[6:8]}"
        return None  # 反將簡算不失效的笛選

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

        # Add dynamic job routes (active jobs only, exclude jobs expiring tomorrow or earlier)
        try:
            today = datetime.now()
            tomorrow = today + timedelta(days=1)
            roc_year_tomorrow = tomorrow.year - 1911
            # 排除明天就截止的職缺，避免 Googlebot 抓取快取時剛好遇到過期
            roc_tomorrow = f"{roc_year_tomorrow}{tomorrow.strftime('%m%d')}"

            stmt = (
                select(JobAllData.id, JobAllData.announce_date, JobAllData.date_from)
                .where(JobAllData.date_to >= roc_tomorrow)
                .order_by(desc(JobAllData.date_from))
                .limit(5000)
            )

            result = await db.execute(stmt)
            jobs = result.all()

            for row in jobs:
                job_id = row.id
                # 優先用公告日期，其次用開始日期，不再 fallback 到 now()
                # 避免 Google 誤認為每天都有新內容
                lastmod = SeoService._format_lastmod(row.announce_date, row.date_from)
                xml_content.append('<url>')
                xml_content.append(f'<loc>{escape(f"{base_url}/job/{job_id}")}</loc>')
                if lastmod:
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
