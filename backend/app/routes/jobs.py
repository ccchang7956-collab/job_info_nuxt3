#jobs.py
from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db
from fastapi.templating import Jinja2Templates
import logging
from datetime import datetime, timedelta  
from operator import itemgetter  # 用於後端排序

import re
import hashlib
import json
from typing import Optional
from app.utils.format_utils import format_place, format_roc_date, extract_rank_range, format_rank_display


logging.basicConfig(level=logging.INFO)

router = APIRouter()
from app.utils.template_utils import templates

from cachetools import TTLCache

# 使用 cachetools 的 TTLCache，設定最大容量 1000 筆，過期時間 300 秒 (5分鐘)
# 這比單純的 dict 更安全，會自動清除過期項目並限制記憶體使用
_query_cache = TTLCache(maxsize=1000, ttl=300)


async def get_jobs_by_date_desc(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(15, ge=1, le=100),  # 新增 per_page 參數
    org: str = Query(None),
    title: str = Query(None),
    sysnam: str = Query(None),
    places: str = Query(None),
    # 改為 Optional[str]，讓空字串也能進入函式
    min_rank: Optional[str] = Query(None),
    max_rank: Optional[str] = Query(None),
    include_history: bool = Query(False),  # 是否包含過期（歷史）職缺
    include_parttime: bool = Query(False),  # 是否包含非正式人員
    sort: str = Query("date_from"),  # 預設排序欄位
    order: str = Query("desc"),      # 預設排序方向
    db: AsyncSession = Depends(get_async_db) # 使用 AsyncSession
):
    # 方法 1：後端轉換，將空字串轉換為 None，然後再轉換成 int
    try:
        min_rank_int = int(min_rank) if min_rank and min_rank.strip() != "" else None
    except ValueError:
        min_rank_int = None
    try:
        max_rank_int = int(max_rank) if max_rank and max_rank.strip() != "" else None
    except ValueError:
        max_rank_int = None

    try:
        offset = (page - 1) * per_page  # 使用動態 per_page
        
        # 生成快取鍵
        cache_key_data = {
            'page': page, 'per_page': per_page, 'org': org, 'title': title, 
            'sysnam': sysnam, 'places': places, 'min_rank': min_rank, 
            'max_rank': max_rank, 'include_history': include_history, 
            'include_parttime': include_parttime, 'sort': sort, 'order': order
        }
        cache_key = hashlib.md5(json.dumps(cache_key_data, sort_keys=True).encode()).hexdigest()
        
        # 檢查快取 (cachetools 會自動處理過期)
        if cache_key in _query_cache:
            cached_result = _query_cache[cache_key]
            return cached_result
        
        filters = []
        if not include_parttime:
            filters.append("sysnam != '無'")
        params = {"limit": per_page, "offset": offset}

        # 取得今天與昨日的民國日期（用於過期判斷）
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        roc_year_today = today.year - 1911
        roc_year_yesterday = yesterday.year - 1911
        roc_today = f"{roc_year_today}{today.strftime('%m%d')}"
        roc_yesterday = f"{roc_year_yesterday}{yesterday.strftime('%m%d')}"

        # 如果不包含歷史職缺，則僅列出尚未過期的資料
        if not include_history:
            filters.append("date_to >= :today")
            params["today"] = roc_today

        if org:
            filters.append("org_name LIKE :org")
            params["org"] = f"%{org}%"
        if title:
            filters.append("title LIKE :title")
            params["title"] = f"%{title}%"
        if sysnam:
            sysnam_list = sysnam.split(",")  # 多選字串以逗號分隔
            sysnam_filters = [f"sysnam LIKE :sysnam_{i}" for i in range(len(sysnam_list))]
            filters.append(f"({' OR '.join(sysnam_filters)})")
            for i, s in enumerate(sysnam_list):
                params[f"sysnam_{i}"] = f"%{s.strip()}%"
        if places:
            place_list = places.split(",")
            place_filters = [f"work_place_type LIKE :place_{i}" for i in range(len(place_list))]
            filters.append(f"({' OR '.join(place_filters)})")
            for i, place in enumerate(place_list):
                params[f"place_{i}"] = f"%{place.strip()}%"

        # 先暫時組成 WHERE 條件，用於接下來的職等過濾查詢
        temp_filters_query = " AND ".join(filters)
        temp_where_clause = f"WHERE {temp_filters_query}" if temp_filters_query else ""

        # 統一查詢 job_all_data
        table_name = "job_all_data"

        # 職等過濾優化：使用資料庫層級的職等範圍查詢
        if min_rank_int is not None or max_rank_int is not None:
            # 使用正則表達式在資料庫層級過濾職等
            rank_patterns = []
            if min_rank_int is not None and max_rank_int is not None:
                # 範圍查詢：找出包含指定範圍的職等
                for i in range(min_rank_int, max_rank_int + 1):
                    rank_patterns.append(f"rank LIKE '%{i}%'")
            elif min_rank_int is not None:
                # 最低職等查詢：找出包含 >= min_rank_int 的職等
                for i in range(min_rank_int, 15):  # 假設最高職等為14
                    rank_patterns.append(f"rank LIKE '%{i}%'")
            elif max_rank_int is not None:
                # 最高職等查詢：找出包含 <= max_rank_int 的職等
                for i in range(1, max_rank_int + 1):
                    rank_patterns.append(f"rank LIKE '%{i}%'")
            
            if rank_patterns:
                filters.append(f"({' OR '.join(rank_patterns)})")

        # 最終組成完整的 WHERE 子句
        filters_query = " AND ".join(filters)
        where_clause = f"WHERE {filters_query}" if filters_query else ""

        # 動態排序設定（限制可排序欄位）
        valid_sort_fields = {
            "org": "org_name",
            "title": "title",
            "sysnam": "sysnam",
            "rank": "rank",
            "place": "work_place_type",
            "date_from": "date_from",
        }
        sort_field = valid_sort_fields.get(sort, "date_from")
        sort_order = "DESC" if order == "desc" else "ASC"
        order_by_clause = f"ORDER BY {sort_field} {sort_order}"

        # 執行職缺查詢
        # 執行職缺查詢
        query = f"""
            SELECT id, org_name AS org, title, sysnam, rank, work_place_type AS place, 
                   date_from, date_to, view_url AS link,
                   (SELECT COUNT(*) FROM job_all_data t2 WHERE t2.org_name = job_all_data.org_name AND t2.work_item = job_all_data.work_item AND t2.id != job_all_data.id AND t2.date_from < job_all_data.date_from) AS history_count
            FROM job_all_data
            {where_clause}
            {order_by_clause}
            LIMIT :limit OFFSET :offset
        """
        # 使用 await 執行查詢
        result = await db.execute(text(query), params)
        jobs = result.fetchall()

        # 查詢各筆職缺的評論數（所有職缺都查 comments）
        job_ids = [job.id for job in jobs]
        comment_counts = {}
        if job_ids:
            comment_query = """
                SELECT job_all_data_id AS job_opening_id, COUNT(*) AS comment_count
                FROM job_comments
                WHERE job_all_data_id IN :job_ids AND is_deleted = 0
                GROUP BY job_all_data_id
            """
            # 使用 await 執行查詢
            comment_counts_result = await db.execute(
                text(comment_query),
                {"job_ids": tuple(job_ids)}
            )
            comment_counts = {row.job_opening_id: row.comment_count for row in comment_counts_result.fetchall()}

        # 整合評論數與職缺資料
        jobs_with_comments = [
            {
                **job._mapping,
                "comment_count": comment_counts.get(job.id, 0),
                "rank_display": format_rank_display(job.rank),
                "place": format_place(job.place), # Format place
                "date_from": format_roc_date(job.date_from), # Format date_from
                "date_to": format_roc_date(job.date_to), # Format date_to
            }
            for job in jobs
        ]

        # 計算分頁資訊 - 優化：只在第一頁或需要時才計算總數
        total_count = None
        if page == 1 or per_page <= 50:  # 第一頁或每頁筆數較少時才計算總數
            total_query = f"SELECT COUNT(*) FROM job_all_data {where_clause}"
            # 使用 await 執行查詢
            total_count_result = await db.execute(text(total_query), params)
            total_count = total_count_result.scalar()
        else:
            # 對於後續頁面，使用估算值或跳過總數計算
            total_count = page * per_page + 100  # 簡單估算
        total_pages = (total_count + per_page - 1) // per_page
        page_range_start = max(1, page - 2)
        page_range_end = min(total_pages, page + 2)
        page_range = list(range(page_range_start, page_range_end + 1))
        page_range_all = list(range(1, total_pages + 1))  # 新增所有頁數範圍

        # 職系資料改為前端寫死，提升效能
        sysnam_admin_list = []
        sysnam_tech_list = []

        response_data = {
            # "request": request, # Remove request from JSON response
            "jobs": jobs_with_comments,
            "current_page": page,
            "per_page": per_page,  # 傳遞 per_page
            "total_pages": total_pages,
            "page_range": page_range,  # 保留原本的分頁範圍
            "page_range_all": page_range_all,  # 新增所有頁數範圍
            "total_count": total_count,
            "sysnam_admin_list": sysnam_admin_list,
            "sysnam_tech_list": sysnam_tech_list,
            "today_date": roc_today,
            "yesterday_date": roc_yesterday
        }
        
        # 儲存到快取（只快取非第一頁的查詢，或可調整策略）
        if page > 1:
            _query_cache[cache_key] = response_data
        
        return response_data
    except Exception as e:
        logging.exception("查詢職缺時發生錯誤：%s", e)
        return {
            "jobs": [],
            "current_page": page,
            "per_page": per_page,
            "total_pages": 0,
            "page_range": [],
            "page_range_all": [],
            "total_count": 0,
            "sysnam_admin_list": [],
            "sysnam_tech_list": [],
            "today_date": '',
            "yesterday_date": ''
        }