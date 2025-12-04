#comment_service.py
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import pytz  # 導入 pytz 用於處理時區
from app.database import get_async_db
from app.models.models import JobComments  # 從自動產生的 models/models.py 匯入 JobComments
from app.schemas import CommentCreate, CommentResponse
import httpx
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import TokenValidationError
import os

# 初始化路由
router = APIRouter()

GOOGLE_RECAPTCHA_SECRET_KEY = os.getenv("GOOGLE_RECAPTCHA_SECRET_KEY", "6LeEYrMqAAAAAJmT3yYXUlebX0j-9HWrdnCANSkh")

async def verify_recaptcha(recaptcha_token: str):
    """
    使用 Google reCAPTCHA API 驗證 (非同步)
    """
    url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {
        "secret": GOOGLE_RECAPTCHA_SECRET_KEY,
        "response": recaptcha_token,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload)
        result = response.json()
    
    print("reCAPTCHA驗證結果:", result)  # Debug
    if not result.get("success"):
        raise HTTPException(status_code=400, detail="reCAPTCHA 驗證失敗")


# 新增留言的路由與業務邏輯
@router.post("/comments", response_model=CommentResponse)
async def submit_comment(
    comment: CommentCreate, 
    request: Request, 
    csrf_protect: CsrfProtect = Depends(), 
    db: AsyncSession = Depends(get_async_db)
):
    try:
        # 從標頭中提取 CSRF Token
        csrf_token = request.headers.get("X-CSRF-Token")
        # print("請求中的 X-CSRF-Token:", csrf_token)
        
        # 驗證 CSRF Token
        if not csrf_token:
             raise HTTPException(status_code=403, detail="缺少 CSRF Token")
        
        csrf_protect.validate_csrf(csrf_token)
        # print("CSRF 驗證成功")
    except TokenValidationError as e:
        print(f"CSRF Token 驗證失敗: {e}")
        raise HTTPException(status_code=403, detail="CSRF 驗證失敗")

    
    
    await verify_recaptcha(comment.recaptcha_token)
    try:
        # 驗證 job_all_data_id 必填
        if not comment.job_all_data_id:
            raise HTTPException(status_code=400, detail="缺少 job_all_data_id")
        # 設置台北時區
        taipei_timezone = pytz.timezone("Asia/Taipei")
        current_time_taipei = datetime.now(taipei_timezone)  # 當前台北時間

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
    except Exception as e:
        await db.rollback() # 發生錯誤時 rollback
        raise HTTPException(status_code=400, detail=f"留言提交失敗: {str(e)}")
