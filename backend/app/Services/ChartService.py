from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any
from app.Utils.FormatUtils import format_place
from cachetools import TTLCache

# Cache for month options (1 hour)
_month_options_cache = TTLCache(maxsize=1, ttl=3600)

class ChartService:
    @staticmethod
    def get_month_options() -> List[Dict[str, str]]:
        if "options" in _month_options_cache:
            return _month_options_cache["options"]
            
        current_date = datetime.now()
        month_options = []
        for i in range(12):
            year = current_date.year - 1911
            formatted_month = f"{year}{current_date.month:02d}"
            month_options.append({
                "value": formatted_month,
                "label": f"{year}年{current_date.month}月"
            })
            current_date = (current_date.replace(day=1) - timedelta(days=1))
        
        _month_options_cache["options"] = month_options
        return month_options

    @staticmethod
    def _get_month_or_default(month: str = None) -> str:
        if month:
            return month
        current_date = datetime.now()
        year = current_date.year - 1911
        return f"{year}{current_date.month:02d}"

    # Cache for chart data (10 minutes)
    _chart_data_cache = TTLCache(maxsize=100, ttl=600)

    @staticmethod
    async def get_top_orgs(db: AsyncSession, month: str = None) -> Dict[str, Any]:
        target_month = ChartService._get_month_or_default(month)
        cache_key = f"top_orgs_{target_month}"
        
        if cache_key in ChartService._chart_data_cache:
            return ChartService._chart_data_cache[cache_key]
        
        query = text("""
            SELECT org_name, COUNT(*) AS job_count
            FROM job_openings
            WHERE date_from LIKE :month
            GROUP BY org_name
            ORDER BY job_count DESC
            LIMIT 10
        """)
        result = await db.execute(query, {"month": f"{target_month}%"})
        results = result.mappings().all()

        data = {
            "org_names": [row["org_name"] for row in results],
            "job_counts": [row["job_count"] for row in results],
            "month": target_month,
            "month_options": ChartService.get_month_options()
        }
        ChartService._chart_data_cache[cache_key] = data
        return data

    @staticmethod
    async def get_top_sysnams(db: AsyncSession, month: str = None) -> Dict[str, Any]:
        target_month = ChartService._get_month_or_default(month)
        cache_key = f"top_sysnams_{target_month}"

        if cache_key in ChartService._chart_data_cache:
            return ChartService._chart_data_cache[cache_key]

        query = text("""
            SELECT sysnam, COUNT(*) AS job_count
            FROM job_openings
            WHERE date_from LIKE :month
            GROUP BY sysnam
            ORDER BY job_count DESC
            LIMIT 10
        """)
        result = await db.execute(query, {"month": f"{target_month}%"})
        results = result.mappings().all()

        data = {
            "sys_names": [row["sysnam"] for row in results],
            "job_counts": [row["job_count"] for row in results],
            "month": target_month,
            "month_options": ChartService.get_month_options()
        }
        ChartService._chart_data_cache[cache_key] = data
        return data

    @staticmethod
    async def get_daily_job_counts(db: AsyncSession, month: str = None) -> Dict[str, Any]:
        target_month = ChartService._get_month_or_default(month)
        cache_key = f"daily_job_counts_{target_month}"

        if cache_key in ChartService._chart_data_cache:
            return ChartService._chart_data_cache[cache_key]

        query = text("""
            SELECT announce_date, COUNT(*) AS job_count
            FROM job_openings
            WHERE announce_date LIKE :month
            GROUP BY announce_date
            ORDER BY announce_date ASC
        """)
        result = await db.execute(query, {"month": f"{target_month}%"})
        results = result.mappings().all()

        data = {
            "dates": [row["announce_date"] for row in results],
            "job_counts": [row["job_count"] for row in results],
            "month": target_month,
            "month_options": ChartService.get_month_options()
        }
        ChartService._chart_data_cache[cache_key] = data
        return data

    @staticmethod
    async def get_workplace_counts(db: AsyncSession, month: str = None) -> Dict[str, Any]:
        target_month = ChartService._get_month_or_default(month)
        cache_key = f"workplace_counts_{target_month}"

        if cache_key in ChartService._chart_data_cache:
            return ChartService._chart_data_cache[cache_key]

        query = text("""
            SELECT work_place_type, COUNT(*) AS job_count
            FROM job_openings
            WHERE date_from LIKE :month
            GROUP BY work_place_type
        """)
        result = await db.execute(query, {"month": f"{target_month}%"})
        results = result.mappings().all()

        workplace_counts = defaultdict(int)
        for row in results:
            raw_place = row["work_place_type"]
            job_count = row["job_count"]
            formatted_place = format_place(raw_place)
            places = formatted_place.split(', ')
            for place in places:
                if place != "N/A":
                    workplace_counts[place] += job_count

        workplace_list = [{"workplace": place, "count": count} for place, count in workplace_counts.items()]
        workplace_list.sort(key=lambda x: x["count"], reverse=True)
        top_workplaces = workplace_list[:10]

        data = {
            "workplace_types": [item["workplace"] for item in top_workplaces],
            "job_counts": [item["count"] for item in top_workplaces],
            "month": target_month,
            "month_options": ChartService.get_month_options()
        }
        ChartService._chart_data_cache[cache_key] = data
        return data

    @staticmethod
    async def get_most_commented_jobs(db: AsyncSession) -> Dict[str, Any]:
        # Cache for 5 minutes as comments might update more frequently
        cache_key = "most_commented_jobs"
        if cache_key in ChartService._chart_data_cache:
            return ChartService._chart_data_cache[cache_key]

        query = text("""
            SELECT jad.id AS id, jad.org_name, jad.title, jad.date_from, jad.date_to, COUNT(jc.id) AS comment_count
            FROM job_all_data jad
            LEFT JOIN job_comments jc ON jad.id = jc.job_all_data_id
            WHERE jc.is_deleted = 0
            GROUP BY jad.id, jad.org_name, jad.title, jad.date_from, jad.date_to
            ORDER BY comment_count DESC
            LIMIT 10
        """)
        result = await db.execute(query)
        data = result.fetchall()

        response = {
            "most_commented_jobs": [dict(row._mapping) for row in data],
        }
        ChartService._chart_data_cache[cache_key] = response
        return response
