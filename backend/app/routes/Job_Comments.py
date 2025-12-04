# Job_Comments.py - 安全版本，修復 SQL 注入風險

from fastapi import APIRouter, Depends, Request, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_async_db
from datetime import datetime
import math
import re
from typing import Optional, List
from app.utils.format_utils import format_roc_date

router = APIRouter()
from app.utils.template_utils import templates

def validate_search_input(input_str: str, max_length: int = 100) -> str:
    """
    驗證搜尋輸入，防止惡意輸入
    """
    if not input_str:
        return ""
    
    # 移除危險字元
    cleaned = re.sub(r'[<>"\';\\]', '', input_str.strip())
    
    # 限制長度
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned

def validate_sysnam_list(sysnam_string: str) -> List[str]:
    """
    驗證職系列表輸入
    """
    if not sysnam_string:
        return []
    
    # 分割並清理
    sysnams = [validate_search_input(s.strip(), 50) for s in sysnam_string.split(',')]
    
    # 過濾空值並限制數量
    valid_sysnams = [s for s in sysnams if s]
    
    # 限制最多選擇 20 個職系
    if len(valid_sysnams) > 20:
        valid_sysnams = valid_sysnams[:20]
    
    return valid_sysnams

async def get_sysnam_lists_for_comments(db: AsyncSession):
    """
    安全地獲取職系列表
    """
    sysnam_admin_list = []
    sysnam_tech_list = []
    
    try:
        # 使用參數化查詢
        admin_query = text("SELECT sysnam FROM job_sysnam WHERE category = :category")
        result_admin = await db.execute(admin_query, {"category": "行政類"})
        admin_results = result_admin.fetchall()
        sysnam_admin_list = [{"sysnam": row.sysnam} for row in admin_results]

        tech_query = text("SELECT sysnam FROM job_sysnam WHERE category = :category")
        result_tech = await db.execute(tech_query, {"category": "技術類"})
        tech_results = result_tech.fetchall()
        sysnam_tech_list = [{"sysnam": row.sysnam} for row in tech_results]
        
    except Exception as e:
        print(f"Error fetching sysnam lists for comments: {e}")
        # 記錄錯誤但不暴露給用戶
        
    return sysnam_admin_list, sysnam_tech_list

class SecureCommentQueryBuilder:
    """
    安全的查詢建構器
    """
    
    def __init__(self):
        self.conditions = []
        self.params = {}
        self.param_counter = 0
    
    def add_condition(self, condition: str, param_name: str, param_value):
        """
        添加安全的查詢條件
        """
        self.conditions.append(condition)
        self.params[param_name] = param_value
    
    def add_like_condition(self, field: str, value: str):
        """
        添加 LIKE 查詢條件
        """
        if value:
            param_name = f"param_{self.param_counter}"
            self.param_counter += 1
            self.add_condition(f"{field} LIKE :{param_name}", param_name, f"%{value}%")
    
    def add_in_condition(self, field: str, values: List[str]):
        """
        添加 IN 查詢條件
        """
        if values:
            param_names = []
            for i, value in enumerate(values):
                param_name = f"param_{self.param_counter}"
                self.param_counter += 1
                param_names.append(f":{param_name}")
                self.params[param_name] = value
            
            condition = f"{field} IN ({', '.join(param_names)})"
            self.conditions.append(condition)
    
    def build_where_clause(self, is_deleted: bool = False):
        """
        建構 WHERE 子句
        """
        all_conditions = [f"c.is_deleted = :is_deleted"] + self.conditions
        is_deleted_param = f"is_deleted_{self.param_counter}"
        self.param_counter += 1
        self.params[is_deleted_param] = 1 if is_deleted else 0
        
        # 更新 is_deleted 參數名稱
        where_clause = " AND ".join(all_conditions).replace(":is_deleted", f":{is_deleted_param}")
        
        return f"WHERE {where_clause}" if all_conditions else ""
    
    def get_params(self):
        """
        獲取所有參數
        """
        return self.params.copy()

@router.get("/Job_Comments", response_class=HTMLResponse)
async def render_comments_page(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    active_page: int = Query(1, ge=1, le=1000, alias="active_page"),
    deleted_page: int = Query(1, ge=1, le=1000, alias="deleted_page"),
    page_size: int = Query(10, ge=5, le=50),  # 限制頁面大小
    show_deleted: bool = Query(False, alias="show_deleted"),
    search_org: Optional[str] = Query(None, alias="search_org"),
    search_title: Optional[str] = Query(None, alias="search_title"),
    search_sysnam: Optional[str] = Query(None, alias="search_sysnam"),
    search_message: Optional[str] = Query(None, alias="search_message")
):
    """
    安全的留言頁面渲染函數
    """
    try:
        # 輸入驗證
        search_org = validate_search_input(search_org or "", 100)
        search_title = validate_search_input(search_title or "", 200)
        search_message = validate_search_input(search_message or "", 500)
        search_sysnam_list = validate_sysnam_list(search_sysnam or "")
        
        # 計算偏移量
        active_offset = (active_page - 1) * page_size
        deleted_offset = (deleted_page - 1) * page_size

        # 基礎查詢欄位
        base_query_fields = """
            c.id AS comment_id, c.message, c.created_at, c.job_all_data_id,
            c.is_deleted, c.deletion_reason,
            jo.org_name, jo.sysnam, jo.title, jo.date_from, jo.date_to
        """
        base_query_from = """
            FROM job_comments c
            JOIN job_all_data jo ON c.job_all_data_id = jo.id
        """

        # 建構安全的查詢條件
        query_builder = SecureCommentQueryBuilder()
        
        if search_org:
            query_builder.add_like_condition("jo.org_name", search_org)
        
        if search_title:
            query_builder.add_like_condition("jo.title", search_title)
        
        if search_sysnam_list:
            query_builder.add_in_condition("jo.sysnam", search_sysnam_list)
        
        if search_message:
            query_builder.add_like_condition("c.message", search_message)

        # 計算總數 - 現有留言
        active_where_clause = query_builder.build_where_clause(is_deleted=False)
        active_count_sql = f"SELECT COUNT(c.id) {base_query_from} {active_where_clause}"
        active_params = query_builder.get_params()
        
        result_active_count = await db.execute(text(active_count_sql), active_params)
        total_active = result_active_count.scalar_one()

        # 計算總數 - 已刪除留言
        deleted_query_builder = SecureCommentQueryBuilder()
        if search_org:
            deleted_query_builder.add_like_condition("jo.org_name", search_org)
        if search_title:
            deleted_query_builder.add_like_condition("jo.title", search_title)
        if search_sysnam_list:
            deleted_query_builder.add_in_condition("jo.sysnam", search_sysnam_list)
        if search_message:
            deleted_query_builder.add_like_condition("c.message", search_message)
        
        deleted_where_clause = deleted_query_builder.build_where_clause(is_deleted=True)
        deleted_count_sql = f"SELECT COUNT(c.id) {base_query_from} {deleted_where_clause}"
        deleted_params = deleted_query_builder.get_params()
        
        result_deleted_count = await db.execute(text(deleted_count_sql), deleted_params)
        total_deleted = result_deleted_count.scalar_one()

        # 計算分頁
        active_total_pages = math.ceil(total_active / page_size) if total_active > 0 else 1
        deleted_total_pages = math.ceil(total_deleted / page_size) if total_deleted > 0 else 1

        current_active_page = min(active_page, active_total_pages) if active_total_pages > 0 else 1
        current_deleted_page = min(deleted_page, deleted_total_pages) if deleted_total_pages > 0 else 1

        active_offset_corrected = (current_active_page - 1) * page_size
        deleted_offset_corrected = (current_deleted_page - 1) * page_size

        # 查詢現有留言數據
        active_data_sql = f"""
            SELECT {base_query_fields}
            {base_query_from}
            {active_where_clause}
            ORDER BY c.created_at DESC
            LIMIT :limit OFFSET :offset
        """
        active_data_params = {
            **active_params,
            "limit": page_size,
            "offset": active_offset_corrected
        }
        result_active_comments = await db.execute(text(active_data_sql), active_data_params)
        active_comments_results = result_active_comments.fetchall()

        # 查詢已刪除留言數據
        deleted_data_sql = f"""
            SELECT {base_query_fields}
            {base_query_from}
            {deleted_where_clause}
            ORDER BY c.created_at DESC
            LIMIT :limit OFFSET :offset
        """
        deleted_data_params = {
            **deleted_params,
            "limit": page_size,
            "offset": deleted_offset_corrected
        }
        result_deleted_comments = await db.execute(text(deleted_data_sql), deleted_data_params)
        deleted_comments_results = result_deleted_comments.fetchall()

        # 處理結果
        active_comments = [dict(row._mapping) for row in active_comments_results]
        deleted_comments = [dict(row._mapping) for row in deleted_comments_results]

        # 計算今天的日期（民國年）
        today = datetime.now()
        roc_year_today = today.year - 1911
        roc_today = f"{roc_year_today:03d}{today.strftime('%m%d')}"

        # 計算分頁範圍
        def calculate_pagination_range(current_page, total_pages, window=2):
            start_page = max(1, current_page - window)
            end_page = min(total_pages, current_page + window)
            return list(range(start_page, end_page + 1)) if total_pages > 0 else []

        active_pagination_range = calculate_pagination_range(current_active_page, active_total_pages)
        deleted_pagination_range = calculate_pagination_range(current_deleted_page, deleted_total_pages)

        # 獲取職系列表
        sysnam_admin_list, sysnam_tech_list = await get_sysnam_lists_for_comments(db)

        return templates.TemplateResponse("Job_Comments.html", {
            "request": request,
            "active_comments": active_comments,
            "deleted_comments": deleted_comments,
            "active_page": current_active_page,
            "deleted_page": current_deleted_page,
            "page_size": page_size,
            "active_total_pages": active_total_pages,
            "deleted_total_pages": deleted_total_pages,
            "active_pagination_range": active_pagination_range,
            "deleted_pagination_range": deleted_pagination_range,
            "active_has_next_page": current_active_page < active_total_pages,
            "active_has_previous_page": current_active_page > 1,
            "deleted_has_next_page": current_deleted_page < deleted_total_pages,
            "deleted_has_previous_page": current_deleted_page > 1,
            "today_date": roc_today,
            "show_deleted": show_deleted,
            "total_active": total_active,
            "total_deleted": total_deleted,
            "search_org": search_org,
            "search_title": search_title,
            "search_sysnam": ', '.join(search_sysnam_list) if search_sysnam_list else "",
            "search_message": search_message,
            "sysnam_admin_list": sysnam_admin_list,
            "sysnam_tech_list": sysnam_tech_list,
        })

    except ValueError as e:
        # 輸入驗證錯誤
        raise HTTPException(status_code=400, detail=f"輸入格式錯誤: {str(e)}")
    
    except Exception as e:
        # 記錄詳細錯誤（在生產環境中應該使用適當的日誌系統）
        print(f"Error in render_comments_page: {e}")
        import traceback
        traceback.print_exc()
        
        # 不向用戶暴露詳細錯誤信息
        raise HTTPException(status_code=500, detail="系統暫時無法處理您的請求，請稍後再試")