from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.Utils.TemplateUtils import templates

router = APIRouter()

@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    """
    關於我們頁面
    """
    return templates.TemplateResponse("about.html", {"request": request})
