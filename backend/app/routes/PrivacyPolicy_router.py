from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# 初始化模板位置
from app.utils.template_utils import templates

# 創建路由實例
router = APIRouter()

@router.get("/PrivacyPolicy", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("PrivacyPolicy.html", {"request": request})
