from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import hashlib
import json
from cachetools import TTLCache
from app.Utils.FormatUtils import format_place, format_roc_date, format_rank_display
import logging

# 使用 cachetools 的 TTLCache
_query_cache = TTLCache(maxsize=1000, ttl=300)

class JobService:
    @staticmethod
    async def get_jobs(
        db: AsyncSession,
        page: int = 1,
        per_page: int = 15,
        org: str = None,
        title: str = None,
        sysnam: str = None,
        places: str = None,
        min_rank: int = None,
        max_rank: int = None,
        include_history: bool = False,
        include_parttime: bool = False,
        sort: str = "date_from",
        order: str = "desc"
    ):
        offset = (page - 1) * per_page
        
        # 生成快取鍵
        cache_key_data = {
            'page': page, 'per_page': per_page, 'org': org, 'title': title, 
            'sysnam': sysnam, 'places': places, 'min_rank': min_rank, 
            'max_rank': max_rank, 'include_history': include_history, 
            'include_parttime': include_parttime, 'sort': sort, 'order': order
        }
        cache_key = hashlib.md5(json.dumps(cache_key_data, sort_keys=True).encode()).hexdigest()
        
        # 檢查快取 (cachetools 會自動處理過期)
        if page > 1 and cache_key in _query_cache:
            return _query_cache[cache_key]
        
        filters = []
        if not include_parttime:
            filters.append("sysnam != '無'")
        params = {"limit": per_page, "offset": offset}

        # 取得今天與昨日的民國日期
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        roc_year_today = today.year - 1911
        roc_year_yesterday = yesterday.year - 1911
        roc_today = f"{roc_year_today}{today.strftime('%m%d')}"
        roc_yesterday = f"{roc_year_yesterday}{yesterday.strftime('%m%d')}"

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
            sysnam_list = [s.strip() for s in sysnam.split(",")]
            # Use IN clause for better performance (uses index)
            filters.append("sysnam IN :sysnam_list")
            params["sysnam_list"] = tuple(sysnam_list) # SQLAlchemy requires tuple for IN

        if places:
            place_list = [p.strip() for p in places.split(",")]
            # Use IN clause for better performance (uses index)
            filters.append("work_place_type IN :place_list")
            params["place_list"] = tuple(place_list)

        # 職等過濾
        if min_rank is not None or max_rank is not None:
            rank_patterns = []
            if min_rank is not None and max_rank is not None:
                for i in range(min_rank, max_rank + 1):
                    rank_patterns.append(f"rank LIKE '%{i}%'")
            elif min_rank is not None:
                for i in range(min_rank, 15):
                    rank_patterns.append(f"rank LIKE '%{i}%'")
            elif max_rank is not None:
                for i in range(1, max_rank + 1):
                    rank_patterns.append(f"rank LIKE '%{i}%'")
            
            if rank_patterns:
                filters.append(f"({' OR '.join(rank_patterns)})")

        filters_query = " AND ".join(filters)
        where_clause = f"WHERE {filters_query}" if filters_query else ""

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

        query = f"""
            SELECT j.id, j.org_name AS org, j.title, j.sysnam, j.rank, j.work_place_type AS place, 
                   j.date_from, j.date_to, j.view_url AS link,
                   (SELECT COUNT(*) FROM job_all_data t2 WHERE t2.org_name = j.org_name AND t2.work_item = j.work_item AND t2.id != j.id AND t2.date_from < j.date_from) AS history_count,
                   (SELECT COUNT(*) FROM job_comments c WHERE c.job_all_data_id = j.id AND c.is_deleted = 0) AS comment_count
            FROM job_all_data j
            {where_clause}
            {order_by_clause}
            LIMIT :limit OFFSET :offset
        """
        
        try:
            result = await db.execute(text(query), params)
            jobs = result.fetchall()

            jobs_with_comments = [
                {
                    **job._mapping,
                    "rank_display": format_rank_display(job.rank),
                    "place": format_place(job.place),
                    "date_from": format_roc_date(job.date_from),
                    "date_to": format_roc_date(job.date_to),
                }
                for job in jobs
            ]

            total_count = None
            if page == 1 or per_page <= 50:
                total_query = f"SELECT COUNT(*) FROM job_all_data {where_clause}"
                total_count_result = await db.execute(text(total_query), params)
                total_count = total_count_result.scalar()
            else:
                total_count = page * per_page + 100

            total_pages = (total_count + per_page - 1) // per_page
            page_range_start = max(1, page - 2)
            page_range_end = min(total_pages, page + 2)
            page_range = list(range(page_range_start, page_range_end + 1))
            page_range_all = list(range(1, total_pages + 1))

            response_data = {
                "jobs": jobs_with_comments,
                "current_page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "page_range": page_range,
                "page_range_all": page_range_all,
                "total_count": total_count,
                "sysnam_admin_list": [],
                "sysnam_tech_list": [],
                "today_date": roc_today,
                "yesterday_date": roc_yesterday
            }
            
            if page > 1:
                _query_cache[cache_key] = response_data
            
            return response_data
            
        except Exception as e:
            logging.exception("Error querying jobs: %s", e)
            raise e

    @staticmethod
    def _process_comments(raw_comments) -> List[dict]:
        comment_dict = {}
        comments = []
        for comment in raw_comments:
            comment_data = {
                "id": comment.id,
                "username": comment.username,
                "initial": comment.initial,
                "message": comment.message,
                "color": comment.color,
                "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S") if comment.created_at else "",
                "parent_id": comment.parent_id,
                "children": []
            }
            comment_dict[comment.id] = comment_data
            
        for comment in comment_dict.values():
            if comment["parent_id"]:
                parent_comment = comment_dict.get(comment["parent_id"])
                if parent_comment:
                    parent_comment["children"].append(comment)
            else:
                comments.append(comment)
        return comments

    @staticmethod
    async def get_job_detail(db: AsyncSession, job_id: int, from_url: str = None):
        try:
            table_name = "job_all_data"
            
            # 1. 查詢職缺資料
            job_query = text(f"SELECT * FROM {table_name} WHERE id = :job_id")
            
            # 2. 查詢留言
            comments_query = text("""
                SELECT id, username, initial, message, color, created_at, parent_id
                FROM job_comments
                WHERE job_all_data_id = :job_id AND is_deleted = 0
                ORDER BY created_at ASC
            """)
            
            import asyncio
            job_task = db.execute(job_query, {"job_id": job_id})
            comments_task = db.execute(comments_query, {"job_id": job_id})
            
            job_result, raw_comments_result = await asyncio.gather(job_task, comments_task)
            job = job_result.fetchone()
            
            if not job:
                return None

            # 3. 查詢重複職缺
            duplicate_query = text(f"""
                SELECT id, org_name, title, date_from, date_to
                FROM {table_name}
                WHERE org_name = :org_name AND work_item = :work_item AND id != :job_id
            """)
            
            duplicates_result = await db.execute(
                duplicate_query,
                {"org_name": job.org_name, "work_item": job.work_item, "job_id": job_id}
            )
            duplicates = duplicates_result.fetchall()

            # 處理留言資料
            comments = JobService._process_comments(raw_comments_result.fetchall())
            
            # 比較日期是否過期
            from app.Utils.FormatUtils import convert_to_gregorian_date
            job_date_to_gregorian = convert_to_gregorian_date(job.date_to)
            current_date = datetime.today().strftime("%Y-%m-%d")
            is_expired = current_date > job_date_to_gregorian
            
            if not from_url:
                from_url = f'/Active_job_openings'
            
            # 轉換 job 為 dict 並格式化地點與日期
            job_dict = dict(job._mapping)
            job_dict["work_place_type"] = format_place(job_dict.get("work_place_type", ""))
            job_dict["date_from"] = format_roc_date(job_dict.get("date_from", ""))
            job_dict["date_to"] = format_roc_date(job_dict.get("date_to", ""))

            # 格式化重複職缺的日期
            formatted_duplicates = []
            for d in duplicates:
                dup_dict = dict(d._mapping)
                dup_dict["date_from"] = format_roc_date(dup_dict.get("date_from", ""))
                dup_dict["date_to"] = format_roc_date(dup_dict.get("date_to", ""))
                formatted_duplicates.append(dup_dict)

            return {
                "job": job_dict, 
                "from_url": from_url,
                "duplicates": formatted_duplicates,
                "comments": comments,
                "is_expired": is_expired
            }
        except Exception as e:
            logging.exception(f"Error in get_job_details: {e}")
            raise e
