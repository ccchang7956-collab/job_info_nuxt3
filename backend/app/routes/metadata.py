from fastapi import APIRouter
from app.utils.get_latest_update_date import get_latest_update_date

router = APIRouter()

@router.get("/last-update")
async def get_last_update():
    date = await get_latest_update_date()
    return {"date": date}
