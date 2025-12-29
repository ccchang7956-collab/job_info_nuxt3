from sqlalchemy import select, distinct, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.Models import JobDataUpdateLog
import math
from typing import Dict, Any

class LogService:
    @staticmethod
    async def get_logs(
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        action: str = None
    ) -> Dict[str, Any]:
        offset = (page - 1) * per_page

        # Build query
        stmt = select(JobDataUpdateLog).order_by(desc(JobDataUpdateLog.start_time))

        if action:
            stmt = stmt.where(JobDataUpdateLog.action == action)

        # Get total count
        count_stmt = select(func.count()).select_from(JobDataUpdateLog)
        if action:
            count_stmt = count_stmt.where(JobDataUpdateLog.action == action)
        
        total_count_result = await db.execute(count_stmt)
        total_count = total_count_result.scalar()

        # Get paginated results
        stmt = stmt.limit(per_page).offset(offset)
        result = await db.execute(stmt)
        logs = result.scalars().all()

        # Get distinct actions for filter
        actions_stmt = select(distinct(JobDataUpdateLog.action))
        actions_result = await db.execute(actions_stmt)
        actions = actions_result.scalars().all()

        # Calculate total pages
        total_pages = math.ceil(total_count / per_page) if total_count else 0
        
        # Generate page range
        page_range_start = max(1, page - 2)
        page_range_end = min(total_pages, page + 2)
        page_range = list(range(page_range_start, page_range_end + 1))

        return {
            "logs": [
                {
                    "id": log.id,
                    "action": log.action,
                    "start_time": log.start_time.strftime("%Y-%m-%d %H:%M:%S") if log.start_time else None,
                    "end_time": log.end_time.strftime("%Y-%m-%d %H:%M:%S") if log.end_time else None,
                    "new_records": log.new_records,
                    "updated_records": log.updated_records,
                    "status": log.status,
                    "remarks": log.remarks
                } for log in logs
            ],
            "actions": actions,
            "current_page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_count": total_count,
            "page_range": page_range
        }
