from collections import defaultdict
import re
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_async_db
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
# Fix import path
from app.utils.template_utils import templates
from app.utils.format_utils import format_place

router = APIRouter()


@router.get("/job_openings_chart", response_class=JSONResponse)
async def get_job_openings_chart(request: Request, month: str = None, db: AsyncSession = Depends(get_async_db)):
    try:
        # 如果未提供月份，使用當前日期的預設值
        if month is None:
            current_date = datetime.now()
            year = current_date.year - 1911  # 西元年轉為民國年
            month = f"{year}{current_date.month:02d}"

        # 動態生成最近 12 個月份選項
        current_date = datetime.now()
        month_options = []
        for i in range(12):  # 最近 12 個月
            year = current_date.year - 1911
            formatted_month = f"{year}{current_date.month:02d}"
            month_options.append({
                "value": formatted_month,
                "label": f"{year}年{current_date.month}月"
            })
            # 減去一個月
            current_date = (current_date.replace(day=1) - timedelta(days=1))

        # 使用原生 SQL 查詢前 10 名機關及其開缺數
        query = text("""
            SELECT org_name, COUNT(*) AS job_count
            FROM job_openings
            WHERE date_from LIKE :month
            GROUP BY org_name
            ORDER BY job_count DESC
            LIMIT 10
        """)
        result = await db.execute(query, {"month": f"{month}%"})
        results = result.mappings().all()  # 確保結果可用列名訪問

        # 將結果分成機關名稱 (org_names) 和開缺數 (job_counts)
        org_names = [row["org_name"] for row in results]
        job_counts = [row["job_count"] for row in results]

        # 傳遞資料給模板
        return {
            "org_names": org_names,
            "job_counts": job_counts,
            "month": month,
            "month_options": month_options  # 將月份選項傳遞給模板
        }
    except Exception as e:
        import traceback
        print(f"Error in get_job_openings_chart: {e}")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e), "traceback": traceback.format_exc()})



@router.get("/job_openings_chart_by_sysnam", response_class=JSONResponse)
async def get_job_openings_sysnam_chart(request: Request, month: str = None, db: AsyncSession = Depends(get_async_db)):
    # 如果未提供月份，使用當前日期的預設值
    if month is None:
        current_date = datetime.now()
        year = current_date.year - 1911  # 西元年轉為民國年
        month = f"{year}{current_date.month:02d}"

    # 動態生成最近 12 個月份選項
    current_date = datetime.now()
    month_options = []
    for i in range(12):  # 最近 12 個月
        year = current_date.year - 1911
        formatted_month = f"{year}{current_date.month:02d}"
        month_options.append({
            "value": formatted_month,
            "label": f"{year}年{current_date.month}月"
        })
        # 減去一個月
        current_date = (current_date.replace(day=1) - timedelta(days=1))

    # 使用原生 SQL 查詢前 10 名職系及其開缺數
    query = text("""
        SELECT sysnam, COUNT(*) AS job_count
        FROM job_openings
        WHERE date_from LIKE :month
        GROUP BY sysnam
        ORDER BY job_count DESC
        LIMIT 10
    """)
    result = await db.execute(query, {"month": f"{month}%"})
    results = result.mappings().all()  # 確保結果可用列名訪問

    # 將結果分成職系名稱 (sys_names) 和開缺數 (job_counts)
    sys_names = [row["sysnam"] for row in results]
    job_counts = [row["job_count"] for row in results]

    # 傳遞資料給模板
    # 傳遞資料給模板
    return {
        "sys_names": sys_names,
        "job_counts": job_counts,
        "month": month,
        "month_options": month_options  # 將月份選項傳遞給模板
    }



@router.get("/job_openings_daily_chart", response_class=JSONResponse)
async def get_job_openings_daily_chart(request: Request, month: str = None, db: AsyncSession = Depends(get_async_db)):
    # 如果未提供月份，使用當前日期的預設值
    if month is None:
        current_date = datetime.now()
        year = current_date.year - 1911  # 西元年轉為民國年
        month = f"{year}{current_date.month:02d}"

    # 動態生成最近 12 個月份選項
    current_date = datetime.now()
    month_options = []
    for i in range(12):  # 最近 12 個月
        year = current_date.year - 1911
        formatted_month = f"{year}{current_date.month:02d}"
        month_options.append({
            "value": formatted_month,
            "label": f"{year}年{current_date.month}月"
        })
        # 減去一個月
        current_date = (current_date.replace(day=1) - timedelta(days=1))

    # 查詢該月份每日新增職缺數量
    query = text("""
        SELECT 
            announce_date,
            COUNT(*) AS job_count
        FROM 
            job_openings
        WHERE 
            announce_date LIKE :month
        GROUP BY 
            announce_date
        ORDER BY 
            announce_date ASC
    """)
    result = await db.execute(query, {"month": f"{month}%"})
    results = result.mappings().all()  # 確保結果可用列名訪問

    # 提取 announce_date 和 job_count
    dates = [row["announce_date"] for row in results]
    job_counts = [row["job_count"] for row in results]

    # 傳遞資料給模板
    # 傳遞資料給模板
    return {
        "dates": dates,
        "job_counts": job_counts,
        "month": month,
        "month_options": month_options
    }




@router.get("/job_openings_workplace_chart", response_class=JSONResponse)
async def get_job_openings_workplace_chart(request: Request, month: str = None, db: AsyncSession = Depends(get_async_db)):
    if month is None:
        current_date = datetime.now()
        year = current_date.year - 1911
        month = f"{year}{current_date.month:02d}"

    # 動態生成最近 12 個月份選項
    current_date = datetime.now()
    month_options = []
    for i in range(12):
        year = current_date.year - 1911
        formatted_month = f"{year}{current_date.month:02d}"
        month_options.append({"value": formatted_month, "label": f"{year}年{current_date.month}月"})
        current_date = (current_date.replace(day=1) - timedelta(days=1))

    # 查詢所有工作地點及其計數（不直接限制前 10 名）
    query = text("""
        SELECT work_place_type, COUNT(*) AS job_count
        FROM job_openings
        WHERE date_from LIKE :month
        GROUP BY work_place_type
    """)
    result = await db.execute(query, {"month": f"{month}%"})
    results = result.mappings().all()

    # 處理多值工作地點並聚合計數（不均分）
    workplace_counts = defaultdict(int)
    for row in results:
        raw_place = row["work_place_type"]
        job_count = row["job_count"]
        # 使用 format_place 處理，並拆分多個地點
        formatted_place = format_place(raw_place)
        places = formatted_place.split(', ')
        # 不均分，每個地點獲得完整計數
        count_per_place = job_count
        for place in places:
            if place != "N/A":
                workplace_counts[place] += count_per_place

    # 轉換為列表並排序，取前 10 名
    workplace_list = [{"workplace": place, "count": count} for place, count in workplace_counts.items()]
    workplace_list.sort(key=lambda x: x["count"], reverse=True)
    top_workplaces = workplace_list[:10]

    # 分離 workplace_types 和 job_counts
    workplace_types = [item["workplace"] for item in top_workplaces]
    job_counts = [item["count"] for item in top_workplaces]

    return {
        "workplace_types": workplace_types,
        "job_counts": job_counts,
        "month": month,
        "month_options": month_options
    }

@router.get("/job_openings_commentscount_chart", response_class=JSONResponse)
async def job_openings_commentscount_chart(request: Request, db: AsyncSession = Depends(get_async_db)):
    try:
        # 查詢最多留言數的職缺
        query = """
            SELECT jad.id AS id, jad.org_name, jad.title, jad.date_from, jad.date_to, COUNT(jc.id) AS comment_count
            FROM job_all_data jad
            LEFT JOIN job_comments jc ON jad.id = jc.job_all_data_id
            WHERE jc.is_deleted = 0
            GROUP BY jad.id, jad.org_name, jad.title, jad.date_from, jad.date_to
            ORDER BY comment_count DESC
            LIMIT 10
        """
        
        result = await db.execute(text(query))
        data = result.fetchall()

        return {
            "most_commented_jobs": [dict(row._mapping) for row in data],
        }
    except Exception as e:
        print(f"Error in job_openings_commentscount_chart: {e}")
        return {
            "most_commented_jobs": [],
        }