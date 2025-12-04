from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from datetime import datetime
import pytz
import httpx
import os
import re
import math
from typing import List, Optional, Tuple
from fastapi import HTTPException
from app.Models.Models import JobComments
from app.Schemas.Schemas import CommentCreate
from app.Utils.FormatUtils import format_roc_date

from cachetools import TTLCache

GOOGLE_RECAPTCHA_SECRET_KEY = os.getenv("GOOGLE_RECAPTCHA_SECRET_KEY", "6LeEYrMqAAAAAJmT3yYXUlebX0j-9HWrdnCANSkh")

# Cache for sysnam lists (1 hour)
_sysnam_cache = TTLCache(maxsize=2, ttl=3600)

class CommentService:
    @staticmethod
    async def verify_recaptcha(recaptcha_token: str, http_client: httpx.AsyncClient = None):
        """
        使用 Google reCAPTCHA API 驗證 (非同步)
        """
        url = "https://www.google.com/recaptcha/api/siteverify"
        payload = {
            "secret": GOOGLE_RECAPTCHA_SECRET_KEY,
            "response": recaptcha_token,
        }
        
        if http_client:
            response = await http_client.post(url, data=payload)
            result = response.json()
        else:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=payload)
                result = response.json()
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail="reCAPTCHA 驗證失敗")

    @staticmethod
    async def create_comment(db: AsyncSession, comment: CommentCreate) -> JobComments:
        # 驗證 job_all_data_id 必填
        if not comment.job_all_data_id:
            raise HTTPException(status_code=400, detail="缺少 job_all_data_id")
        
        # 設置台北時區
        taipei_timezone = pytz.timezone("Asia/Taipei")
        current_time_taipei = datetime.now(taipei_timezone)

        # 如果 user_id 為 None，設置為訪客模式
        username = comment.username or "訪客"
        user_id = comment.user_id

        # 建立新留言物件
        new_comment = JobComments(
            user_id=user_id,
            username=username,
            initial=username[0].upper(),
            message=comment.message,
            color=comment.color,
            created_at=current_time_taipei,
            email=comment.email or "",
            job_all_data_id=comment.job_all_data_id,
            parent_id=comment.parent_id,
            is_deleted=False
        )
        # 儲存至資料庫
        db.add(new_comment)
        await db.commit()
        await db.refresh(new_comment)
        return new_comment

    @staticmethod
    def validate_search_input(input_str: str, max_length: int = 100) -> str:
        if not input_str:
            return ""
        # 移除危險字元
        cleaned = re.sub(r'[<>"\';\\]', '', input_str.strip())
        # 限制長度
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
        return cleaned

    @staticmethod
    def validate_sysnam_list(sysnam_string: str) -> List[str]:
        if not sysnam_string:
            return []
        sysnams = [CommentService.validate_search_input(s.strip(), 50) for s in sysnam_string.split(',')]
        valid_sysnams = [s for s in sysnams if s]
        if len(valid_sysnams) > 20:
            valid_sysnams = valid_sysnams[:20]
        return valid_sysnams

    @staticmethod
    async def get_sysnam_lists(db: AsyncSession) -> Tuple[List[str], List[str]]:
        if "admin" in _sysnam_cache and "tech" in _sysnam_cache:
            return _sysnam_cache["admin"], _sysnam_cache["tech"]

        sysnam_admin_list = []
        sysnam_tech_list = []
        try:
            admin_query = text("SELECT sysnam FROM job_sysnam WHERE category = :category")
            result_admin = await db.execute(admin_query, {"category": "行政類"})
            sysnam_admin_list = [row.sysnam for row in result_admin.fetchall()]

            tech_query = text("SELECT sysnam FROM job_sysnam WHERE category = :category")
            result_tech = await db.execute(tech_query, {"category": "技術類"})
            sysnam_tech_list = [row.sysnam for row in result_tech.fetchall()]
            
            _sysnam_cache["admin"] = sysnam_admin_list
            _sysnam_cache["tech"] = sysnam_tech_list
        except Exception as e:
            print(f"Error fetching sysnam lists: {e}")
        return sysnam_admin_list, sysnam_tech_list

    @staticmethod
    async def get_comments_list(
        db: AsyncSession,
        page: int = 1,
        per_page: int = 10,
        show_deleted: bool = False,
        search_org: str = None,
        search_title: str = None,
        search_sysnam: str = None,
        search_message: str = None
    ):
        # 輸入驗證
        search_org = CommentService.validate_search_input(search_org or "", 100)
        search_title = CommentService.validate_search_input(search_title or "", 200)
        search_message = CommentService.validate_search_input(search_message or "", 500)
        search_sysnam_list = CommentService.validate_sysnam_list(search_sysnam or "")
        
        offset = (page - 1) * per_page

        base_query_fields = """
            c.id AS comment_id, c.message, c.created_at, c.job_all_data_id,
            c.is_deleted, c.deletion_reason,
            jo.org_name, jo.sysnam, jo.title, jo.date_from, jo.date_to, jo.rank
        """
        base_query_from = """
            FROM job_comments c
            JOIN job_all_data jo ON c.job_all_data_id = jo.id
        """

        conditions = []
        params = {}
        param_counter = 0

        if search_org:
            conditions.append(f"jo.org_name LIKE :param_{param_counter}")
            params[f"param_{param_counter}"] = f"%{search_org}%"
            param_counter += 1
        
        if search_title:
            conditions.append(f"jo.title LIKE :param_{param_counter}")
            params[f"param_{param_counter}"] = f"%{search_title}%"
            param_counter += 1
        
        if search_sysnam_list:
            in_params = []
            for s in search_sysnam_list:
                in_params.append(f":param_{param_counter}")
                params[f"param_{param_counter}"] = s
                param_counter += 1
            conditions.append(f"jo.sysnam IN ({', '.join(in_params)})")
        
        if search_message:
            conditions.append(f"c.message LIKE :param_{param_counter}")
            params[f"param_{param_counter}"] = f"%{search_message}%"
            param_counter += 1

        # Build WHERE clause
        conditions.insert(0, f"c.is_deleted = :is_deleted_param")
        params["is_deleted_param"] = 1 if show_deleted else 0
        
        where_clause = "WHERE " + " AND ".join(conditions)

        # Count
        count_sql = f"SELECT COUNT(c.id) {base_query_from} {where_clause}"
        result_count = await db.execute(text(count_sql), params)
        total_count = result_count.scalar_one()

        # Pagination
        total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
        current_page = min(page, total_pages) if total_pages > 0 else 1
        offset_corrected = (current_page - 1) * per_page

        # Data
        data_sql = f"""
            SELECT {base_query_fields}
            {base_query_from}
            {where_clause}
            ORDER BY c.created_at DESC
            LIMIT :limit OFFSET :offset
        """
        params["limit"] = per_page
        params["offset"] = offset_corrected
        
        result_comments = await db.execute(text(data_sql), params)
        comments_results = result_comments.fetchall()

        comments = []
        for row in comments_results:
            comment = dict(row._mapping)
            if comment.get('created_at'):
                comment['created_at'] = comment['created_at'].strftime("%Y-%m-%d %H:%M:%S")
            if comment.get('date_from'):
                comment['date_from'] = format_roc_date(comment['date_from'])
            if comment.get('date_to'):
                comment['date_to'] = format_roc_date(comment['date_to'])
            comments.append(comment)

        sysnam_admin_list, sysnam_tech_list = await CommentService.get_sysnam_lists(db)

        return {
            "comments": comments,
            "current_page": current_page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_count": total_count,
            "sysnam_admin_list": sysnam_admin_list,
            "sysnam_tech_list": sysnam_tech_list
        }
