from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_async_db  # 資料庫連線設定
from fastapi.responses import JSONResponse


# 建立 APIRouter 用來處理路由
router = APIRouter()

# 從資料庫取得所有的 Actions（去重）
async def get_actions(db: AsyncSession):
    query = text("SELECT DISTINCT action FROM job_data_update_log ORDER BY action")
    result = await db.execute(query)
    return [row[0] for row in result.fetchall()]

# 從資料庫取得日誌資料（支援分頁和篩選）
async def get_logs(db: AsyncSession, page: int, page_size: int, action_filter: str = None):
    offset = (page - 1) * page_size
    base_query = """
        SELECT
            id, action, start_time, end_time, new_records, updated_records,
            status, remarks  -- <<< 修改：增加 remarks 欄位
        FROM job_data_update_log
    """
    if action_filter:
        base_query += " WHERE action = :action_filter"
    base_query += " ORDER BY start_time DESC LIMIT :page_size OFFSET :offset"

    params = {"page_size": page_size, "offset": offset}
    if action_filter:
        params["action_filter"] = action_filter

    query = text(base_query)
    result = await db.execute(query, params)
    # 使用 mappings() 可以自動將查詢結果轉為字典列表，包含所有選取的欄位
    return [dict(row) for row in result.mappings()]

# 計算總頁數
async def get_total_pages(db: AsyncSession, page_size: int, action_filter: str = None):
    base_query = "SELECT COUNT(*) FROM job_data_update_log"
    if action_filter:
        base_query += " WHERE action = :action_filter"

    params = {}
    if action_filter:
        params["action_filter"] = action_filter

    query = text(base_query)
    result = await db.execute(query, params)
    total_records = result.scalar()
    return math.ceil(total_records / page_size)


def get_pagination_range(current_page: int, total_pages: int, display_range: int = 10):
    """
    計算顯示的頁碼範圍，預設顯示附近 10 個頁碼。
    """
    # 計算起始和結束頁碼範圍
    start_page = max(1, current_page - (display_range // 2))
    end_page = min(total_pages, start_page + display_range - 1)

    # 調整範圍，確保顯示固定數量的頁碼（若可能）
    if end_page - start_page + 1 < display_range:
        start_page = max(1, end_page - display_range + 1)

    return list(range(start_page, end_page + 1))


@router.get("/log", response_class=JSONResponse)
async def log_page(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    page: int = Query(1, ge=1),
    action: str = Query(None)
):
    page_size = 15  # 每頁顯示筆數
    logs = await get_logs(db, page, page_size, action) # logs 現在會包含 remarks
    total_pages = await get_total_pages(db, page_size, action)
    actions = await get_actions(db)

    # 計算頁碼範圍，固定顯示 10 個頁碼
    pagination_range = get_pagination_range(current_page=page, total_pages=total_pages, display_range=10)

    return {
        "logs": logs,
        "current_page": page,
        "total_pages": total_pages,
        "pagination_range": pagination_range,
        "actions": actions,
        "selected_action": action
    }