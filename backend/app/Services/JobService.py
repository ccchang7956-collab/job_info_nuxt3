from sqlalchemy import select, func, or_, desc, asc, case, literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from datetime import datetime, timedelta
import hashlib
import json
import re
from typing import List, Dict, Any, Tuple
from cachetools import TTLCache
from app.Utils.FormatUtils import format_place, format_roc_date, format_rank_display
from app.Models.Models import JobAllData, JobComments
import logging

# 使用 cachetools 的 TTLCache
_query_cache = TTLCache(maxsize=1000, ttl=300)
# 日期快取 (1小時過期)
_date_cache = TTLCache(maxsize=1, ttl=3600)


def get_roc_dates() -> Tuple[str, str]:
    """
    取得今日與昨日的民國日期，使用快取避免重複計算
    Returns: (roc_today, roc_yesterday)
    """
    cache_key = "roc_dates"
    if cache_key in _date_cache:
        cached = _date_cache[cache_key]
        # 檢查是否仍為同一天
        if cached["date"] == datetime.now().date():
            return cached["roc_today"], cached["roc_yesterday"]
    
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    roc_year_today = today.year - 1911
    roc_year_yesterday = yesterday.year - 1911
    roc_today = f"{roc_year_today}{today.strftime('%m%d')}"
    roc_yesterday = f"{roc_year_yesterday}{yesterday.strftime('%m%d')}"
    
    _date_cache[cache_key] = {
        "date": today.date(),
        "roc_today": roc_today,
        "roc_yesterday": roc_yesterday
    }
    return roc_today, roc_yesterday


def escape_like_pattern(value: str) -> str:
    """
    轉義 LIKE 查詢中的特殊字元 (% 和 _)
    使用方括號包裝模式（SQLite 支援）
    """
    if not value:
        return value
    return value.replace('%', '[%]').replace('_', '[_]')


def parse_rank_range(rank_str: str) -> Tuple[int, int]:
    """
    解析職等字串，提取最小與最大職等
    例如: "5-7" -> (5, 7), "5" -> (5, 5)
    """
    if not rank_str:
        return (0, 0)
    
    # 移除非數字與非連字號的字元
    cleaned = re.sub(r'[^0-9\-]', ' ', rank_str)
    numbers = re.findall(r'\d+', cleaned)
    
    if not numbers:
        return (0, 0)
    
    nums = [int(n) for n in numbers if 1 <= int(n) <= 14]
    if not nums:
        return (0, 0)
    
    return (min(nums), max(nums))

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
        if cache_key in _query_cache:
            return _query_cache[cache_key]
        
        # 建立查詢
        stmt = select(JobAllData)
        
        # 1. 篩選條件
        conditions = []
        
        if not include_parttime:
            conditions.append(JobAllData.sysnam != '無')

        # 取得今天與昨日的民國日期 (使用快取)
        roc_today, roc_yesterday = get_roc_dates()

        if not include_history:
            conditions.append(JobAllData.date_to >= roc_today)

        if org:
            escaped_org = escape_like_pattern(org)
            conditions.append(JobAllData.org_name.like(f"%{escaped_org}%"))
        if title:
            escaped_title = escape_like_pattern(title)
            conditions.append(JobAllData.title.like(f"%{escaped_title}%"))
        if sysnam:
            sysnam_list = [s.strip() for s in sysnam.split(",")]
            conditions.append(JobAllData.sysnam.in_(sysnam_list))

        if places:
            place_list = [p.strip() for p in places.split(",")]
            place_conditions = [JobAllData.work_place_type.like(f"%{escape_like_pattern(p)}%") for p in place_list]
            if place_conditions:
                conditions.append(or_(*place_conditions))

        # 職等過濾 (使用 LIKE 模式匹配，支援多種格式)
        if min_rank is not None or max_rank is not None:
            start_rank = min_rank if min_rank is not None else 1
            end_rank = max_rank if max_rank is not None else 14
            start_rank = max(1, min(14, start_rank))
            end_rank = max(1, min(14, end_rank))
            
            # 職等格式範例:
            # "薦任第8職等至薦任第9職等"
            # "委任第5職等"
            # "5-7"
            rank_conditions = []
            for i in range(start_rank, end_rank + 1):
                # 匹配 "第X職等" 格式 (薦任第8職等、委任第5職等)
                rank_conditions.append(JobAllData.rank.like(f"%第{i}職等%"))
                # 匹配純數字格式 (5-7, 第5-7職等)
                if i < 10:
                    # 單位數需排除 10-14 的誤判
                    rank_conditions.append(JobAllData.rank.like(f"%第{i}-%"))
                    rank_conditions.append(JobAllData.rank.like(f"%-{i}職等%"))
            if rank_conditions:
                conditions.append(or_(*rank_conditions))

        if conditions:
            stmt = stmt.where(*conditions)

        # 2. 排序
        sort_columns = {
            "org": JobAllData.org_name,
            "title": JobAllData.title,
            "sysnam": JobAllData.sysnam,
            "rank": JobAllData.rank,
            "place": JobAllData.work_place_type,
            "date_from": JobAllData.date_from,
        }
        
        sort_col = sort_columns.get(sort, JobAllData.date_from)
        if order == "desc":
            stmt = stmt.order_by(desc(sort_col))
        else:
            stmt = stmt.order_by(asc(sort_col))

        # 3. 處理 Subqueries (歷史職缺數與留言數)
        # 使用 aliased 建立 correlated subquery 進行計數
        # 這比 LEFT JOIN + GROUP BY 更適合分頁場景，因為只計算當頁資料的計數
        
        # History Count: 同機關同職務的歷史職缺數
        J2 = aliased(JobAllData)
        history_count_subq = (
             select(func.count())
             .select_from(J2)
             .where(
                 J2.org_name == JobAllData.org_name,
                 J2.work_item == JobAllData.work_item,
                 J2.id != JobAllData.id,
                 J2.date_from < JobAllData.date_from
             )
             .correlate(JobAllData)
             .scalar_subquery()
        )

        # Comment Count: 該職缺的留言數 (未刪除)
        comment_count_subq = (
            select(func.count())
            .select_from(JobComments)
            .where(
                JobComments.job_all_data_id == JobAllData.id,
                JobComments.is_deleted == 0
            )
            .correlate(JobAllData)
            .scalar_subquery()
        )
        
        # 建立包含計數的查詢語句
        stmt_with_counts = select(
            JobAllData,
            history_count_subq.label("history_count"),
            comment_count_subq.label("comment_count")
        )
        
        # 套用篩選條件
        if conditions:
            stmt_with_counts = stmt_with_counts.where(*conditions)

        # Re-apply order by to the new statement
        if order == "desc":
            stmt_with_counts = stmt_with_counts.order_by(desc(sort_col))
        else:
            stmt_with_counts = stmt_with_counts.order_by(asc(sort_col))
            
        # 4. 分頁與執行主查詢
        stmt_paginated = stmt_with_counts.limit(per_page).offset(offset)
        
        try:
            result = await db.execute(stmt_paginated)
            rows = result.all() # [(JobAllData, history_count, comment_count), ...]

            jobs_with_comments = []
            for row in rows:
                job, result_history_count, result_comment_count = row
                
                # Transform to dict
                job_dict = {
                    "id": job.id,
                    "org": job.org_name, # Keep 'org' for backward compatibility if needed
                    "org_name": job.org_name, # Added for Pydantic schema
                    "title": job.title,
                    "sysnam": job.sysnam,
                    "rank": job.rank,
                    "place": job.work_place_type, # Keep 'place' for backward compatibility
                    "work_place_type": job.work_place_type, # Added for Pydantic schema
                    "work_item": job.work_item, # Added for Pydantic schema
                    "date_from": job.date_from,
                    "date_to": job.date_to,
                    "link": job.view_url, # Keep 'link' for backward compatibility
                    "view_url": job.view_url, # Added for Pydantic schema
                    "announce_date": job.announce_date, # Added for Pydantic schema
                    "contact_method": job.contact_method, # Added for Pydantic schema
                    # Personnel fields
                    "person_kind": job.person_kind,
                    "number_of": job.number_of,
                    "reserve_num": job.reserve_num,
                    # Add formatted fields
                    "rank_display": format_rank_display(job.rank),
                    # "place" is overwritten below with formatted value, take care
                    
                    "history_count": result_history_count,
                    "comment_count": result_comment_count,
                    
                    # Original mapping included these formatted dates
                    "date_from": format_roc_date(job.date_from),
                    "date_to": format_roc_date(job.date_to),
                }
                # Overwrite place with formatted value as per original logic
                job_dict["place"] = format_place(job.work_place_type)
                
                jobs_with_comments.append(job_dict)

            # 5. 計算總筆數
            total_count = None
            if page == 1 or per_page <= 50:
                 # Count query
                 count_stmt = select(func.count()).select_from(JobAllData)
                 if conditions:
                     count_stmt = count_stmt.where(*conditions)
                 
                 total_count_result = await db.execute(count_stmt)
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
            # 1. 查詢職缺資料
            stmt = select(JobAllData).where(JobAllData.id == job_id)
            result = await db.execute(stmt)
            job = result.scalar_one_or_none()
            
            if not job:
                return None
            
            # 2. 查詢留言
            comments_stmt = (
                select(JobComments)
                .where(
                    JobComments.job_all_data_id == job_id,
                    JobComments.is_deleted == 0
                )
                .order_by(asc(JobComments.created_at))
            )
            comments_result = await db.execute(comments_stmt)
            raw_comments = comments_result.scalars().all()

            # 3. 查詢重複職缺
            duplicate_stmt = (
                select(JobAllData)
                .where(
                    JobAllData.org_name == job.org_name,
                    JobAllData.work_item == job.work_item,
                    JobAllData.id != job_id
                )
            )
            duplicates_result = await db.execute(duplicate_stmt)
            duplicates = duplicates_result.scalars().all()

            # 處理留言資料
            comments = JobService._process_comments(raw_comments)
            
            # 比較日期是否過期
            from app.Utils.FormatUtils import convert_to_gregorian_date
            job_date_to_gregorian = convert_to_gregorian_date(job.date_to)
            current_date = datetime.today().strftime("%Y-%m-%d")
            is_expired = current_date > job_date_to_gregorian
            
            if not from_url:
                from_url = f'/Active_job_openings'
            
            # Helper function to convert ORM object to dict
            def orm_to_dict(obj):
                return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
            
            # 轉換 job 為 dict 並格式化地點與日期
            job_dict = {
                **orm_to_dict(job),
                "work_place_type": format_place(job.work_place_type) if job.work_place_type else "",
                "date_from": format_roc_date(job.date_from) if job.date_from else "",
                "date_to": format_roc_date(job.date_to) if job.date_to else ""
            }

            # 格式化重複職缺的日期
            formatted_duplicates = []
            for d in duplicates:
                dup_dict = {
                    **orm_to_dict(d),
                    "date_from": format_roc_date(d.date_from) if d.date_from else "",
                    "date_to": format_roc_date(d.date_to) if d.date_to else ""
                }
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
