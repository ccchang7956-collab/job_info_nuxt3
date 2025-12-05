# LINE_AI/Line_ai_db_service.py
import os
import logging
from sqlalchemy import text
from app.Core.Database import AsyncSessionLocal # Import from app.Core.Database
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def _normalize_place_for_query(place_str: Optional[str]) -> Optional[str]:
    if not place_str:
        return None
    # Ensure we always work with '臺'
    normalized = place_str.replace('台', '臺') 
    if normalized.endswith("市") or normalized.endswith("縣"):
        return normalized[:-1] # Remove 市 or 縣 for broader matching (e.g. "臺北" matches "臺北市")
    return normalized

async def query_job_openings_from_db(
    sysnam_list: Optional[List[str]] = None,
    location_list: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    
    has_sysnam_criteria = bool(sysnam_list and any(s.strip() for s in sysnam_list))
    has_location_criteria = bool(location_list and any(l.strip() for l in location_list))

    logger.info(f"DB service received query for sysnam_list: {sysnam_list}, location_list: {location_list}")

    if not has_sysnam_criteria and not has_location_criteria:
        logger.info("No search criteria (sysnam_list or location_list) provided for job query in db_service.")
        return []

    async with AsyncSessionLocal() as session:
        try:
            query_base = """
                SELECT id, announce_date, org_name, title, sysnam, person_kind, rank,
                       number_of, gender_type, work_place_type, date_from, date_to,
                       type, vitae_email, work_quality, work_item, work_address,
                       contact_method, url_link, view_url, work_type
                FROM job_all_data
                WHERE 1=1
            """
            conditions = []
            params = {}

            if has_sysnam_criteria and sysnam_list:
                sysnam_conditions = []
                for i, s_item in enumerate(sysnam_list):
                    stripped_s_item = s_item.strip()
                    if stripped_s_item:
                        logger.debug(f"Adding sysnam condition for: '{stripped_s_item}'")
                        sysnam_conditions.append(f"sysnam LIKE :sysnam_{i}")
                        params[f"sysnam_{i}"] = f"%{stripped_s_item}%"
                if sysnam_conditions:
                    conditions.append(f"({' OR '.join(sysnam_conditions)})")
            
            if has_location_criteria and location_list:
                location_query_conditions = []
                logger.debug(f"Original location_list for DB processing: {location_list}")
                for i, loc_item in enumerate(location_list):
                    stripped_loc_item = loc_item.strip()
                    if stripped_loc_item:
                        standardized_loc_item = stripped_loc_item.replace('台', '臺')
                        normalized_location_for_query = _normalize_place_for_query(standardized_loc_item)
                        
                        logger.debug(f"Normalizing location '{standardized_loc_item}' to '{normalized_location_for_query}' for DB LIKE clause.")
                        
                        if normalized_location_for_query: 
                            location_query_conditions.append(
                                f"(REPLACE(work_place_type, '台', '臺') LIKE :loc_{i} OR REPLACE(work_address, '台', '臺') LIKE :loc_{i})"
                            )
                            params[f"loc_{i}"] = f"%{normalized_location_for_query}%"
                if location_query_conditions:
                    conditions.append(f"({' OR '.join(location_query_conditions)})")
            
            if not conditions: 
                logger.warning("No valid SQL conditions generated for DB query despite initial checks.")
                return []

            query_base += " AND " + " AND ".join(conditions)
            
            # --- MODIFIED ORDER BY CLAUSE (USING DIRECT STRING SORT FOR YYYMMDD) ---
            query_base += " ORDER BY date_from DESC, id DESC LIMIT 50" 
            # --- END OF MODIFIED ORDER BY CLAUSE ---
            
            logger.info(f"Executing DB query (raw): {query_base} with params: {params}")

            result = await session.execute(text(query_base), params)
            # Convert rows to dicts
            all_results = [dict(row) for row in result.mappings()]
            
            logger.info(f"DB query returned {len(all_results)} results (sorted by date_from string DESC).")
            
            if not all_results and (has_sysnam_criteria or has_location_criteria):
                logger.warning(f"Query returned 0 results. Criteria used - sysnam: {sysnam_list}, location: {location_list}.")

            return all_results
            
        except Exception as e:
            logger.error(f"Unexpected error during DB query: {e}", exc_info=True)
            return [{"error_message": "查詢職缺時發生未知錯誤。"}]