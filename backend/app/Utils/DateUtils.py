from sqlalchemy import text
from app.Core.Database import AsyncSessionLocal
from datetime import datetime
import asyncio
import logging

class TimedCache:
    def __init__(self):
        self.cached_value = None
        self.last_updated = None
        self.lock = asyncio.Lock()

    def should_update(self):
        now = datetime.now()
        
        # 如果從未更新，直接返回 True
        if self.last_updated is None:
            return True
        
        # 如果日期不同，直接更新
        if now.date() != self.last_updated.date():
            return True
        
        # 如果距離上次更新超過一定時間（例如 4 小時），觸發更新
        time_elapsed = (now - self.last_updated).total_seconds()
        if time_elapsed > 4 * 3600:  # 4 小時 = 4 * 3600 秒
            return True
        
        return False

    async def get_value(self):
        # Double-checked locking pattern for async
        if self.should_update():
            async with self.lock:
                if self.should_update():
                    self.cached_value = await fetch_latest_update_date()
                    self.last_updated = datetime.now()
        return self.cached_value

# 實例化快取
cache = TimedCache()

async def fetch_latest_update_date():
    async with AsyncSessionLocal() as db:
        try:
            query = text("""
                SELECT end_time 
                FROM job_data_update_log 
                WHERE action = '篩選正式職缺' 
                ORDER BY end_time DESC 
                LIMIT 1
            """)
            result = await db.execute(query)
            row = result.fetchone()
            if row and row[0]:
                dt = row[0]
                roc_year = dt.year - 1911
                formatted_date = f"{roc_year:03d}/{dt.month:02d}/{dt.day:02d}"
                return formatted_date
            return "114/02/22"
        except Exception as e:
            logging.error(f"Error fetching update date: {e}")
            return "114/02/22"

async def get_latest_update_date():
    return await cache.get_value()
