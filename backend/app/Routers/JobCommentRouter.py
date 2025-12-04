from fastapi import APIRouter, Depends, Request, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.Core.Database import get_async_db
from app.Services.CommentService import CommentService
from app.Utils.TemplateUtils import templates

router = APIRouter()

@router.get("/Job_Comments", response_class=HTMLResponse)
async def render_comments_page(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    active_page: int = Query(1, ge=1, le=1000, alias="active_page"),
    deleted_page: int = Query(1, ge=1, le=1000, alias="deleted_page"),
    page_size: int = Query(10, ge=5, le=50),
    show_deleted: bool = Query(False, alias="show_deleted"),
    search_org: Optional[str] = Query(None, alias="search_org"),
    search_title: Optional[str] = Query(None, alias="search_title"),
    search_sysnam: Optional[str] = Query(None, alias="search_sysnam"),
    search_message: Optional[str] = Query(None, alias="search_message")
):
    try:
        # Fetch active comments
        active_result = await CommentService.get_comments_list(
            db=db, page=active_page, per_page=page_size, show_deleted=False,
            search_org=search_org, search_title=search_title, 
            search_sysnam=search_sysnam, search_message=search_message
        )
        
        # Fetch deleted comments
        deleted_result = await CommentService.get_comments_list(
            db=db, page=deleted_page, per_page=page_size, show_deleted=True,
            search_org=search_org, search_title=search_title, 
            search_sysnam=search_sysnam, search_message=search_message
        )

        # Calculate pagination ranges
        def calculate_pagination_range(current_page, total_pages, window=2):
            start_page = max(1, current_page - window)
            end_page = min(total_pages, current_page + window)
            return list(range(start_page, end_page + 1)) if total_pages > 0 else []

        active_pagination_range = calculate_pagination_range(active_result['current_page'], active_result['total_pages'])
        deleted_pagination_range = calculate_pagination_range(deleted_result['current_page'], deleted_result['total_pages'])

        # Date for display
        today = datetime.now()
        roc_year_today = today.year - 1911
        roc_today = f"{roc_year_today:03d}{today.strftime('%m%d')}"

        return templates.TemplateResponse("Job_Comments.html", {
            "request": request,
            "active_comments": active_result['comments'],
            "deleted_comments": deleted_result['comments'],
            "active_page": active_result['current_page'],
            "deleted_page": deleted_result['current_page'],
            "page_size": page_size,
            "active_total_pages": active_result['total_pages'],
            "deleted_total_pages": deleted_result['total_pages'],
            "active_pagination_range": active_pagination_range,
            "deleted_pagination_range": deleted_pagination_range,
            "active_has_next_page": active_result['current_page'] < active_result['total_pages'],
            "active_has_previous_page": active_result['current_page'] > 1,
            "deleted_has_next_page": deleted_result['current_page'] < deleted_result['total_pages'],
            "deleted_has_previous_page": deleted_result['current_page'] > 1,
            "today_date": roc_today,
            "show_deleted": show_deleted,
            "total_active": active_result['total_count'],
            "total_deleted": deleted_result['total_count'],
            "search_org": search_org,
            "search_title": search_title,
            "search_sysnam": search_sysnam,
            "search_message": search_message,
            "sysnam_admin_list": [{"sysnam": s} for s in active_result['sysnam_admin_list']], # Template expects dicts?
            "sysnam_tech_list": [{"sysnam": s} for s in active_result['sysnam_tech_list']],
        })

    except Exception as e:
        print(f"Error in render_comments_page: {e}")
        raise HTTPException(status_code=500, detail="系統暫時無法處理您的請求，請稍後再試")
