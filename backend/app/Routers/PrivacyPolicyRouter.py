from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse# 初始化模板位置
from app.Utils.TemplateUtils import templates

router = APIRouter()

@router.get("/PrivacyPolicy", response_class=HTMLResponse)
async def privacy_policy_page(request: Request):
    return templates.TemplateResponse("PrivacyPolicy.html", {"request": request})
