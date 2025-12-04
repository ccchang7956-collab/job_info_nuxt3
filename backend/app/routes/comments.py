from fastapi import APIRouter, Depends, Request, Query, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_async_db
from datetime import datetime
import math
import re
from typing import Optional, List
from app.utils.format_utils import format_roc_date

router = APIRouter()

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
        sysnam_admin_list = [row.sysnam for row in admin_results]

        tech_query = text("SELECT sysnam FROM job_sysnam WHERE category = :category")
        result_tech = await db.execute(tech_query, {"category": "技術類"})
        tech_results = result_tech.fetchall()
        sysnam_tech_list = [row.sysnam for row in tech_results]
        
    except Exception as e:
        print(f"Error fetching sysnam lists for comments: {e}")
        
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

@router.get("/comments/list", response_class=JSONResponse)
async def get_comments_list(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    page: int = Query(1, ge=1, le=1000),
    per_page: int = Query(10, ge=5, le=50),
    show_deleted: bool = Query(False),
    search_org: Optional[str] = Query(None),
    search_title: Optional[str] = Query(None),
    search_sysnam: Optional[str] = Query(None),
    search_message: Optional[str] = Query(None)
):
    try:
        # 輸入驗證
        search_org = validate_search_input(search_org or "", 100)
        search_title = validate_search_input(search_title or "", 200)
        search_message = validate_search_input(search_message or "", 500)
        search_sysnam_list = validate_sysnam_list(search_sysnam or "")
        
        # 計算偏移量
        offset = (page - 1) * per_page

        # 基礎查詢欄位
        base_query_fields = """
            c.id AS comment_id, c.message, c.created_at, c.job_all_data_id,
            c.is_deleted, c.deletion_reason,
            jo.org_name, jo.sysnam, jo.title, jo.date_from, jo.date_to, jo.rank
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

        # 計算總數
        where_clause = query_builder.build_where_clause(is_deleted=show_deleted)
        count_sql = f"SELECT COUNT(c.id) {base_query_from} {where_clause}"
        params = query_builder.get_params()
        
        result_count = await db.execute(text(count_sql), params)
        total_count = result_count.scalar_one()

        # 計算分頁
        total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
        current_page = min(page, total_pages) if total_pages > 0 else 1
        offset_corrected = (current_page - 1) * per_page

        # 查詢留言數據
        data_sql = f"""
            SELECT {base_query_fields}
            {base_query_from}
            {where_clause}
            ORDER BY c.created_at DESC
            LIMIT :limit OFFSET :offset
        """
        data_params = {
            **params,
            "limit": per_page,
            "offset": offset_corrected
        }
        result_comments = await db.execute(text(data_sql), data_params)
        comments_results = result_comments.fetchall()

        # 處理結果
        comments = []
        for row in comments_results:
            comment = dict(row._mapping)
            # Format datetime
            if comment.get('created_at'):
                comment['created_at'] = comment['created_at'].strftime("%Y-%m-%d %H:%M:%S")
            
            # Format ROC dates
            if comment.get('date_from'):
                comment['date_from'] = format_roc_date(comment['date_from'])
            if comment.get('date_to'):
                comment['date_to'] = format_roc_date(comment['date_to'])
                
            comments.append(comment)

        # 獲取職系列表 (for filters)
        sysnam_admin_list, sysnam_tech_list = await get_sysnam_lists_for_comments(db)

        return {
            "comments": comments,
            "current_page": current_page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_count": total_count,
            "sysnam_admin_list": sysnam_admin_list,
            "sysnam_tech_list": sysnam_tech_list
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"輸入格式錯誤: {str(e)}")
    
    except Exception as e:
        print(f"Error in get_comments_list: {e}")
        raise HTTPException(status_code=500, detail="系統暫時無法處理您的請求，請稍後再試")
