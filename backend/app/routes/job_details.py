from fastapi import APIRouter, Request, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.database import get_async_db  # 引入資料庫連線
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from app.utils.format_utils import format_place, format_roc_date, convert_to_gregorian_date, convert_to_gregorian_date_iso  

from fastapi.responses import JSONResponse
router = APIRouter()

@router.get("/Active_job_openings/{job_id}")
async def get_job_details(request: Request, job_id: int, from_url: str = None, include_parttime: bool = Query(False), db: Session = Depends(get_async_db)):
    try:
        table_name = "job_all_data"
        
        # 1. 查詢職缺資料
        job_query = text(f"SELECT * FROM {table_name} WHERE id = :job_id")
        
        # 2. 查詢留言 (預先準備 SQL)
        comments_query = text("""
            SELECT id, username, initial, message, color, created_at, parent_id
            FROM job_comments
            WHERE job_all_data_id = :job_id AND is_deleted = 0
            ORDER BY created_at ASC
        """)

        # 執行並行查詢 (職缺與留言)
        # 注意：重複職缺查詢依賴於職缺資料 (org_name, work_item)，所以需分兩階段或改寫 SQL
        # 這裡先查職缺，確認存在後再查重複與留言，但留言其實可以跟職缺一起查，只是若職缺不存在查留言也沒用
        # 為了最大化效能，我們將職缺查詢與留言查詢並行，若職缺不存在再拋出錯誤
        
        job_task = db.execute(job_query, {"job_id": job_id})
        comments_task = db.execute(comments_query, {"job_id": job_id})
        
        import asyncio
        job_result, raw_comments_result = await asyncio.gather(job_task, comments_task)
        
        job = job_result.fetchone()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # 3. 查詢重複職缺 (依賴 job 資料)
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
        raw_comments = raw_comments_result.fetchall()
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
        
        # 比較日期是否過期
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

        response_data = {
            "job": job_dict, 
            "from_url": from_url,
            "duplicates": formatted_duplicates,
            "comments": comments,
            "is_expired": is_expired
        }
        
        response = JSONResponse(content=response_data)
        expire_time = (datetime.now() + timedelta(hours=1)).strftime("%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie(key=f"job_viewed_{job_id}", value="1", expires=expire_time)
        return response
    except Exception as e:
        import logging
        logging.exception(f"Error in get_job_details: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pass
