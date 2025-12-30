from fastapi import APIRouter, Depends, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.Core.Database import get_async_db
from app.Services.CommentService import CommentService
from app.Services.CsrfService import verify_csrf
from app.Schemas.Schemas import CommentCreate, CommentResponse, CommentListResponse

router = APIRouter()

@router.post("", response_model=CommentResponse)
async def submit_comment(
    comment: CommentCreate, 
    request: Request, 
    csrf_valid: bool = Depends(verify_csrf),
    db: AsyncSession = Depends(get_async_db)
):
    http_client = getattr(request.app.state, "http_client", None)
    await CommentService.verify_recaptcha(comment.recaptcha_token, http_client)
    
    try:
        return await CommentService.create_comment(db, comment)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"留言提交失敗: {str(e)}")

@router.get("/list", response_model=CommentListResponse)
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
        return await CommentService.get_comments_list(
            db=db,
            page=page,
            per_page=per_page,
            show_deleted=show_deleted,
            search_org=search_org,
            search_title=search_title,
            search_sysnam=search_sysnam,
            search_message=search_message
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"輸入格式錯誤: {str(e)}")
    except Exception as e:
        import logging
        logging.error(f"Error in get_comments_list: {e}")
        raise HTTPException(status_code=500, detail="系統暫時無法處理您的請求，請稍後再試")
