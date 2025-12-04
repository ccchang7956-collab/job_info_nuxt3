from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from cachetools import TTLCache

# Cache sitemap for 1 hour (3600 seconds)
sitemap_cache = TTLCache(maxsize=1, ttl=3600)

class SeoService:
    @staticmethod
    def get_robots_txt() -> str:
        return """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /private/

Sitemap: https://www.opendgpa.site/sitemap.xml
"""

    @staticmethod
    async def get_sitemap_xml(db: AsyncSession) -> str:
        # Check cache first
        if "sitemap" in sitemap_cache:
            return sitemap_cache["sitemap"]

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
            
        # Add dynamic job routes (Active jobs only)
        try:
            query = text("""
                SELECT id, date_from 
                FROM job_all_data 
                WHERE date_to >= :today 
                ORDER BY date_from DESC 
                LIMIT 5000
            """)
            
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
        
        return final_content
