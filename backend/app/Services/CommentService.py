from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc, text
from datetime import datetime
import pytz
import httpx
import logging
import re
import math
import bleach
from typing import List, Optional, Tuple, Dict, Any
from fastapi import HTTPException
from app.Models.Models import JobComments, JobAllData, JobSysnam
from app.Schemas.Schemas import CommentCreate
from app.Utils.FormatUtils import format_roc_date

from cachetools import TTLCache
from app.Core.Config import Config

# Use config for Turnstile key
CLOUDFLARE_TURNSTILE_SECRET_KEY = Config.CLOUDFLARE_TURNSTILE_SECRET_KEY

# Cache for sysnam lists (1 hour)
_sysnam_cache = TTLCache(maxsize=2, ttl=3600)


def sanitize_html(text: str) -> str:
    """
    清理 HTML 標籤，防止 XSS 攻擊
    只保留純文字，移除所有 HTML 標籤
    """
    if not text:
        return ""
    # 移除所有 HTML 標籤
    return bleach.clean(text, tags=[], attributes={}, strip=True)


class CommentService:
    @staticmethod
    async def verify_turnstile(token: str, http_client: httpx.AsyncClient = None):
        """
        使用 Cloudflare Turnstile API 驗證 (非同步)
        """
        url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
        payload = {
            "secret": CLOUDFLARE_TURNSTILE_SECRET_KEY,
            "response": token,
        }
        
        if http_client:
            response = await http_client.post(url, data=payload)
            result = response.json()
        else:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=payload)
                result = response.json()
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail="Turnstile 驗證失敗")

    @staticmethod
    async def create_comment(db: AsyncSession, comment: CommentCreate) -> JobComments:
        # 驗證 job_all_data_id 必填
        if not comment.job_all_data_id:
            raise HTTPException(status_code=400, detail="缺少 job_all_data_id")
        
        # 設置台北時區
        taipei_timezone = pytz.timezone("Asia/Taipei")
        current_time_taipei = datetime.now(taipei_timezone)

        # 如果 user_id 為 None，設置為訪客模式
        # 清理使用者輸入以防止 XSS
        username = sanitize_html(comment.username) or "訪客"
        safe_message = sanitize_html(comment.message)
        user_id = comment.user_id

        # 建立新留言物件
        new_comment = JobComments(
            user_id=user_id,
            username=username,
            initial=username[0].upper(),
            message=safe_message,
            color=comment.color,
            created_at=current_time_taipei,
            email=comment.email or "",
            job_all_data_id=comment.job_all_data_id,
            parent_id=comment.parent_id,
            is_deleted=0
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
        cleaned = re.sub(r'[<>"\';]', '', input_str.strip())
        # 限制長度
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
        return cleaned

    @staticmethod
    def escape_like_pattern(value: str) -> str:
        """轉義 LIKE 查詢中的特殊字元 (% 和 _)"""
        if not value:
            return value
        return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

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
            # ORM Refactor
            admin_stmt = select(JobSysnam.sysnam).where(JobSysnam.category == "行政類")
            result_admin = await db.execute(admin_stmt)
            sysnam_admin_list = result_admin.scalars().all()

            tech_stmt = select(JobSysnam.sysnam).where(JobSysnam.category == "技術類")
            result_tech = await db.execute(tech_stmt)
            sysnam_tech_list = result_tech.scalars().all()
            
            _sysnam_cache["admin"] = sysnam_admin_list
            _sysnam_cache["tech"] = sysnam_tech_list
        except Exception as e:
            logging.error(f"Error fetching sysnam lists: {e}")
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

        # ORM Query Construction
        stmt = (
            select(JobComments, JobAllData)
            .join(JobAllData, JobComments.job_all_data_id == JobAllData.id)
        )

        conditions = []
        
        # Filter by display status
        if show_deleted:
            conditions.append(JobComments.is_deleted == 1)
        else:
            conditions.append(JobComments.is_deleted == 0)

        if search_org:
            escaped_org = CommentService.escape_like_pattern(search_org)
            conditions.append(JobAllData.org_name.like(f"%{escaped_org}%", escape='\\'))
        
        if search_title:
            escaped_title = CommentService.escape_like_pattern(search_title)
            conditions.append(JobAllData.title.like(f"%{escaped_title}%", escape='\\'))
        
        if search_sysnam_list:
            conditions.append(JobAllData.sysnam.in_(search_sysnam_list))
        
        if search_message:
            escaped_message = CommentService.escape_like_pattern(search_message)
            conditions.append(JobComments.message.like(f"%{escaped_message}%", escape='\\'))

        if conditions:
            stmt = stmt.where(*conditions)

        # Count Query
        # Note: SQLAlchemy 1.4/2.0+ idiom for count is select(func.count()).select_from(...)
        count_stmt = select(func.count()).select_from(JobComments).join(JobAllData, JobComments.job_all_data_id == JobAllData.id)
        if conditions:
            count_stmt = count_stmt.where(*conditions)
            
        result_count = await db.execute(count_stmt)
        total_count = result_count.scalar()

        # Pagination
        total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
        current_page = min(page, total_pages) if total_pages > 0 else 1
        offset_corrected = (current_page - 1) * per_page

        # Data Query
        stmt = stmt.order_by(desc(JobComments.created_at)).limit(per_page).offset(offset_corrected)
        
        result_comments = await db.execute(stmt)
        rows = result_comments.all()

        comments = []
        for row in rows:
            comment, job = row
            # Mapping based on Schemas.CommentItem
            comment_dict = {
                "comment_id": comment.id,
                "message": comment.message,
                "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S") if comment.created_at else "",
                "job_all_data_id": comment.job_all_data_id,
                "is_deleted": comment.is_deleted,
                "deletion_reason": comment.deletion_reason,
                
                # Joined fields from JobAllData
                "org_name": job.org_name,
                "sysnam": job.sysnam,
                "title": job.title,
                "date_from": format_roc_date(job.date_from),
                "date_to": format_roc_date(job.date_to),
                "rank": job.rank,
                
                # User fields
                "user_id": comment.user_id,
                "username": comment.username,
                "initial": comment.initial,
                "color": comment.color,
                "email": comment.email,
                "parent_id": comment.parent_id
            }
            comments.append(comment_dict)

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
