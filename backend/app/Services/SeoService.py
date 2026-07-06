from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from cachetools import TTLCache
from app.Models.Models import JobAllData
from app.Utils.FormatUtils import convert_to_gregorian_date
import logging
import os
import asyncio
import httpx
from typing import Optional, List
from xml.sax.saxutils import escape
from urllib.parse import quote
import re

# Cache sitemap for 30 minutes (1800 seconds)
# 縮短快cache，讓失效 URL 更快實際被清除，减少 Googlebot 抓到 404 的機率
sitemap_cache = TTLCache(maxsize=10, ttl=1800)

SITE_DOMAIN = os.getenv("SITE_DOMAIN", "https://opendgpa.shibaalin.com").rstrip("/")

# 靜態頁面的最後修改日期（固定值，不隨每次呼叫變動）
# 避免 Google 每次都誤認為「有新內容」，降低信任度
STATIC_PAGE_LASTMOD = {
    "/": "2025-12-30",
    "/comments": "2025-12-30",
    "/charts": "2025-12-30",
    "/about": "2025-12-30",
    "/privacy-policy": "2025-06-01",
}

# 台灣 22 縣市
PLACES = [
    '臺北市', '新北市', '基隆市', '桃園市', '新竹縣', '新竹市', '苗栗縣',
    '臺中市', '彰化縣', '南投縣', '雲林縣', '嘉義縣', '嘉義市', '臺南市',
    '高雄市', '屏東縣', '宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣', '金門縣', '連江縣'
]

# 熱門職系
SYSNAMS = [
    '綜合行政', '人事行政', '經建行政', '會計審計', '地政', '社勞行政', '文教行政', '社會工作', '法制', '交通行政',
    '土木工程', '電機工程', '資訊處理', '農業技術', '測量製圖', '建築工程', '機械工程', '都市計畫'
]

# IndexNow API 設定
INDEXNOW_KEY = os.getenv("INDEXNOW_KEY", "")
INDEXNOW_ENDPOINT = "https://api.indexnow.org/IndexNow"

# Sitemap 每頁 URL 數量
SITEMAP_PAGE_SIZE = 1000


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
    def _format_lastmod(date_str=None, fallback_date_str=None) -> Optional[str]:
        """將民國日期 (YYYMMDD) 或西元日期 (YYYYMMDD) 轉成 ISO 8601 日期。
        優先使用 date_str，若為空則嘗試 fallback_date_str，
        兩者都為空才回傳 None（由呼叫方決定要舊 fallback）。
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
        return None

    @staticmethod
    async def get_sitemap_index() -> str:
        """生成 Sitemap Index XML，列出所有子 sitemap。"""
        cache_key = "sitemap_index"
        if cache_key in sitemap_cache:
            return sitemap_cache[cache_key]

        base_url = SITE_DOMAIN

        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_parts.append('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

        # 靜態頁面 sitemap
        static_lastmod = max(STATIC_PAGE_LASTMOD.values())
        xml_parts.append('<sitemap>')
        xml_parts.append(f'<loc>{escape(base_url)}/sitemap-static.xml</loc>')
        xml_parts.append(f'<lastmod>{static_lastmod}</lastmod>')
        xml_parts.append('</sitemap>')

        # 職缺 sitemap（從 DB 取得總數計算頁數）
        # 預設先放第一頁，後續由 get_sitemap_job_page 決定實際頁數
        # 這裡用快取的分頁數量
        total_pages = sitemap_cache.get("jobs_total_pages", 1)
        for page in range(1, total_pages + 1):
            xml_parts.append('<sitemap>')
            xml_parts.append(f'<loc>{escape(base_url)}/sitemap-jobs-{page}.xml</loc>')
            xml_parts.append('</sitemap>')

        xml_parts.append('</sitemapindex>')

        result = "\n".join(xml_parts)
        sitemap_cache[cache_key] = result
        return result

    @staticmethod
    async def get_sitemap_static() -> str:
        """生成靜態及長青分類頁面的 Sitemap XML。"""
        cache_key = "sitemap_static"
        if cache_key in sitemap_cache:
            return sitemap_cache[cache_key]

        base_url = SITE_DOMAIN
        
        static_routes = [
            {"path": "/", "priority": "1.0", "changefreq": "daily"},
            {"path": "/comments", "priority": "0.7", "changefreq": "daily"},
            {"path": "/charts", "priority": "0.7", "changefreq": "daily"},
            {"path": "/about", "priority": "0.5", "changefreq": "monthly"},
            {"path": "/privacy-policy", "priority": "0.3", "changefreq": "yearly"},
        ]

        today_str = datetime.now().strftime("%Y-%m-%d")

        # 台灣 22 縣市
        for p in PLACES:
            static_routes.append({"path": f"/places/{quote(p)}", "priority": "0.9", "changefreq": "daily", "lastmod": today_str})

        # 熱門職系
        for s in SYSNAMS:
            static_routes.append({"path": f"/sysnams/{quote(s)}", "priority": "0.9", "changefreq": "daily", "lastmod": today_str})

        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_parts.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

        for route in static_routes:
            lastmod = route.get("lastmod") or STATIC_PAGE_LASTMOD.get(route["path"], "2025-12-30")
            xml_parts.append('<url>')
            xml_parts.append(f'<loc>{escape(base_url + route["path"])}</loc>')
            xml_parts.append(f'<lastmod>{lastmod}</lastmod>')
            xml_parts.append(f'<changefreq>{route["changefreq"]}</changefreq>')
            xml_parts.append(f'<priority>{route["priority"]}</priority>')
            xml_parts.append('</url>')

        xml_parts.append('</urlset>')
        result = "\n".join(xml_parts)
        sitemap_cache[cache_key] = result
        return result

    @staticmethod
    async def get_sitemap_jobs_page(db: AsyncSession, page: int) -> Optional[str]:
        """生成指定分頁的職缺 Sitemap XML。每頁最多 SITEMAP_PAGE_SIZE 筆。"""
        cache_key = f"sitemap_jobs_{page}"
        if cache_key in sitemap_cache:
            return sitemap_cache[cache_key]

        base_url = SITE_DOMAIN
        offset = (page - 1) * SITEMAP_PAGE_SIZE

        try:
            today = datetime.now()
            tomorrow = today + timedelta(days=1)
            roc_year_tomorrow = tomorrow.year - 1911
            roc_tomorrow = f"{roc_year_tomorrow}{tomorrow.strftime('%m%d')}"

            # 先取總數（只做一次，快取結果）
            if "jobs_total_count" not in sitemap_cache:
                from sqlalchemy import func
                count_stmt = (
                    select(func.count(JobAllData.id))
                    .where(JobAllData.date_to >= roc_tomorrow)
                )
                count_result = await db.execute(count_stmt)
                total_count = count_result.scalar() or 0
                sitemap_cache["jobs_total_count"] = total_count
                total_pages = max(1, (total_count + SITEMAP_PAGE_SIZE - 1) // SITEMAP_PAGE_SIZE)
                sitemap_cache["jobs_total_pages"] = total_pages

            total_count = sitemap_cache["jobs_total_count"]
            total_pages = sitemap_cache["jobs_total_pages"]

            # 頁碼超出範圍
            if page > total_pages:
                return None

            stmt = (
                select(JobAllData.id, JobAllData.announce_date, JobAllData.date_from)
                .where(JobAllData.date_to >= roc_tomorrow)
                .order_by(desc(JobAllData.date_from))
                .limit(SITEMAP_PAGE_SIZE)
                .offset(offset)
            )

            result = await db.execute(stmt)
            jobs = result.all()

            xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
            xml_parts.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

            for row in jobs:
                job_id = row.id
                lastmod = SeoService._format_lastmod(row.announce_date, row.date_from)
                xml_parts.append('<url>')
                xml_parts.append(f'<loc>{escape(f"{base_url}/job/{job_id}")}</loc>')
                if lastmod:
                    xml_parts.append(f'<lastmod>{lastmod}</lastmod>')
                xml_parts.append('<changefreq>weekly</changefreq>')
                xml_parts.append('<priority>0.8</priority>')
                xml_parts.append('</url>')

            xml_parts.append('</urlset>')

            final_content = "\n".join(xml_parts)
            sitemap_cache[cache_key] = final_content
            return final_content

        except Exception as e:
            logging.error(f"Error generating sitemap jobs page {page}: {e}")
            return None

    @staticmethod
    async def get_sitemap_xml(db: AsyncSession) -> str:
        """向下相容：產生完整 Sitemap（兼容舊有路由，現在實際回傳 Sitemap Index）。"""
        return await SeoService.get_sitemap_index()

    @staticmethod
    def invalidate_sitemap_cache():
        """清除 sitemap 快取（新職缺入庫後呼叫）。"""
        keys_to_delete = [k for k in sitemap_cache.keys()
                          if str(k).startswith("sitemap") or k in ("jobs_total_count", "jobs_total_pages")]
        for key in keys_to_delete:
            sitemap_cache.pop(key, None)
        logging.info("Sitemap cache invalidated.")

    # =========================================================================
    # IndexNow — 主動推送新 URL 給搜尋引擎（Bing / Yandex / Seznam）
    # =========================================================================

    @staticmethod
    async def push_indexnow(job_ids: List[int], http_client: httpx.AsyncClient) -> bool:
        """將新上架的職缺 URL 推送到 IndexNow。
        
        Args:
            job_ids: 新職缺的 ID 列表
            http_client: httpx.AsyncClient 實例
        
        Returns:
            True 表示推送成功，False 表示失敗或未設定 KEY。
        """
        if not INDEXNOW_KEY:
            logging.warning("INDEXNOW_KEY not set, skipping IndexNow push.")
            return False

        if not job_ids:
            return True

        urls = [f"{SITE_DOMAIN}/job/{job_id}" for job_id in job_ids]

        # IndexNow 每次最多 10,000 筆，分批推送
        batch_size = 100
        success = True

        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            payload = {
                "host": SITE_DOMAIN.replace("https://", "").replace("http://", ""),
                "key": INDEXNOW_KEY,
                "keyLocation": f"{SITE_DOMAIN}/{INDEXNOW_KEY}.txt",
                "urlList": batch
            }
            try:
                response = await http_client.post(
                    INDEXNOW_ENDPOINT,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=15.0
                )
                if response.status_code in (200, 202):
                    logging.info(f"IndexNow: pushed {len(batch)} URLs, status={response.status_code}")
                else:
                    logging.warning(f"IndexNow: unexpected status {response.status_code}: {response.text[:200]}")
                    success = False
            except Exception as e:
                logging.error(f"IndexNow push failed: {e}")
                success = False

        return success

    # =========================================================================
    # SEO Health Check
    # =========================================================================

    @staticmethod
    async def get_seo_health(http_client: httpx.AsyncClient) -> dict:
        """檢查 SEO 基礎設施健康狀態。
        
        策略：直接驗證本地生成的 sitemap 內容，不依賴 HTTP 呼叫，
        避免 SITE_DOMAIN 在開發環境指向無效 URL 導致誤報。
        """
        results = {}

        # ── 驗證 robots.txt ───────────────────────────────────────────────
        try:
            robots_content = SeoService.get_robots_txt()
            ok = all(keyword in robots_content for keyword in ["User-agent:", "Sitemap:"])
            results["robots_txt"] = {
                "ok": ok,
                "content_length": len(robots_content),
                "has_sitemap_directive": "Sitemap:" in robots_content,
                "has_llms_txt": "LLMs:" in robots_content,
            }
        except Exception as e:
            results["robots_txt"] = {"ok": False, "error": str(e)}

        # ── 驗證靜態 Sitemap ──────────────────────────────────────────────
        try:
            static_content = await SeoService.get_sitemap_static()
            required_paths = ["/", "/about", "/comments", "/charts", "/privacy-policy"]
            found_paths = all(path in static_content for path in required_paths)
            # 確保主要靜態頁面 lastmod 不是今天（允許分類/職系等長青頁面為今天）
            from datetime import date
            today = date.today().isoformat()
            base_url = SITE_DOMAIN
            
            no_today_lastmod = True
            for path in required_paths:
                escaped_loc = re.escape(escape(base_url + path))
                pattern = rf"<loc>{escaped_loc}</loc>\s*<lastmod>{re.escape(today)}</lastmod>"
                if re.search(pattern, static_content):
                    no_today_lastmod = False
                    break

            results["sitemap_static"] = {
                "ok": found_paths and no_today_lastmod,
                "content_length": len(static_content),
                "all_paths_present": found_paths,
                "lastmod_is_fixed": no_today_lastmod,
            }
        except Exception as e:
            results["sitemap_static"] = {"ok": False, "error": str(e)}

        # ── 驗證 Sitemap Index ─────────────────────────────────────────────
        try:
            index_content = await SeoService.get_sitemap_index()
            has_sitemapindex = "sitemapindex" in index_content
            has_static_ref = "sitemap-static.xml" in index_content
            results["sitemap_index"] = {
                "ok": has_sitemapindex and has_static_ref,
                "content_length": len(index_content),
                "is_sitemapindex_format": has_sitemapindex,
                "has_static_sitemap": has_static_ref,
                "total_job_pages": sitemap_cache.get("jobs_total_pages", "not_computed"),
            }
        except Exception as e:
            results["sitemap_index"] = {"ok": False, "error": str(e)}

        # ── 外部連通性（非阻塞式，使用生產 domain 確認） ─────────────────
        external_ok = False
        if SITE_DOMAIN and not SITE_DOMAIN.startswith("http://localhost"):
            try:
                resp = await http_client.get(
                    f"{SITE_DOMAIN}/robots.txt",
                    timeout=5.0,
                    follow_redirects=True
                )
                external_ok = resp.status_code == 200
                results["external_robots"] = {
                    "ok": external_ok,
                    "url": f"{SITE_DOMAIN}/robots.txt",
                    "status": resp.status_code,
                }
            except Exception as e:
                results["external_robots"] = {
                    "ok": False,
                    "url": f"{SITE_DOMAIN}/robots.txt",
                    "error": "Connection failed (expected in dev environment)"
                }
        else:
            results["external_robots"] = {
                "ok": True,  # 開發環境跳過外部檢查
                "note": "Skipped in dev environment (SITE_DOMAIN is localhost)"
            }

        overall_ok = all(v["ok"] for v in results.values())
        return {
            "status": "healthy" if overall_ok else "degraded",
            "checks": results,
            "indexnow_configured": bool(INDEXNOW_KEY),
            "site_domain": SITE_DOMAIN,
            "cache_stats": {
                "jobs_total_count": sitemap_cache.get("jobs_total_count", 0),
                "jobs_total_pages": sitemap_cache.get("jobs_total_pages", 0),
                "cached_keys": list(sitemap_cache.keys()),
            }
        }
