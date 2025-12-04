from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.Core.Database import get_db

router = APIRouter()

@router.get("/api/search-sysnam/")
async def search_sysnam(query: str, session: Session = Depends(get_db)):
    # 查詢符合的職系名稱
    search_query = """
        SELECT DISTINCT sysnam
        FROM job_sysnam
        WHERE sysnam LIKE :query
        LIMIT 10
    """
    results = session.execute(text(search_query), {"query": f"%{query}%"}).fetchall()
    return {"suggestions": [row.sysnam for row in results]}
