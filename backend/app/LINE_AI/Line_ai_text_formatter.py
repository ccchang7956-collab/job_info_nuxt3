# LINE_AI/Line_ai_text_formatter.py
from typing import List, Dict, Any, Optional, Tuple
import logging # 確保 logging 已 import
import json
import re
from datetime import datetime

# --- Logger 初始化 ---
# 將 logger 初始化移到 try-except 區塊之前
logger = logging.getLogger(__name__)
# --- End Logger 初始化 ---

# --- 從 FormatUtils 匯入 ---
try:
    from app.Utils.FormatUtils import format_place, normalize_place
except ImportError:
    logger.error("Failed to import FormatUtils. Ensure 'Utils' directory is accessible from the project root in PYTHONPATH.")
    # 提供一個假的 format_place 和 normalize_place 以避免執行時崩潰，但功能會不完整
    def format_place(place_str: str) -> str:
        logger.warning("Using mock format_place due to import error.")
        return place_str if place_str else "N/A"
    def normalize_place(input_str: str) -> str:
        logger.warning("Using mock normalize_place due to import error.")
        return input_str
# --- End 從 FormatUtils 匯入 ---


# --- Helper Functions ---

def _format_roc_date_for_display(date_str: Optional[str]) -> str:
    if date_str and isinstance(date_str, str) and len(date_str) == 7 and date_str.isdigit():
        return f"{date_str[0:3]}/{date_str[3:5]}/{date_str[5:7]}"
    if date_str and isinstance(date_str, str) and (date_str.count('/') == 2 or date_str.count('-') == 2):
        return date_str
    return date_str or "-"

def _extract_rank_range(rank_text: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    if not rank_text or not isinstance(rank_text, str):
        return None, None
    numbers = list(map(int, re.findall(r'(?:第\s*)?(\d+)(?=\s*(?:職|等))', rank_text)))
    if not numbers:
        numbers = list(map(int, re.findall(r'(\d+)\s*等', rank_text))) # For cases like "約聘5等"
        if not numbers:
            numbers = list(map(int, re.findall(r'\d+', rank_text))) # Fallback to any number
            if not numbers:
                 return None, None
    return min(numbers), max(numbers)

def _format_rank_display(rank_text: Optional[str]) -> str:
    if not rank_text or not isinstance(rank_text, str) :
        return "-"
    
    rmin, rmax = _extract_rank_range(rank_text)
    
    if rmin is None or rmax is None:
        cleaned_rank_text = rank_text.replace("相當", "").strip()
        if len(cleaned_rank_text) > 15:
            return cleaned_rank_text[:13] + "..."
        return cleaned_rank_text if cleaned_rank_text else "-"
        
    if rmin == rmax:
        return f"{rmin}等"
    else:
        return f"{rmin}等 - {rmax}等"

def _format_place_for_display(work_place_str_from_db: Optional[str]) -> str:
    """
    格式化地點字串供顯示用。
    1. 使用 utils.format_utils.format_place 進行基本格式化。
    2. 使用 utils.format_utils.normalize_place 將「台」轉為「臺」。
    3. 進行長度裁剪。
    """
    if not work_place_str_from_db:
        return "未提供"

    # 1. 使用 utils.format_utils.format_place 進行格式化
    formatted_by_util = format_place(work_place_str_from_db)

    if formatted_by_util == "N/A":
        return "未提供"

    # 2. 將「台」轉為「臺」
    normalized_by_util = normalize_place(formatted_by_util)
    
    display_place = normalized_by_util

    # 3. 長度裁剪
    if len(display_place) > 25:
        return display_place[:23] + "..."
    
    return display_place if display_place else "未提供"


def _is_active_job(date_to_str: Optional[str]) -> bool:
    """
    Checks if a job is active based on its 'date_to' string (ROC format).
    'date_to_str' is expected in 'YYYMMDD' ROC format (e.g., '1130520').
    """
    if not date_to_str or not isinstance(date_to_str, str) or len(date_to_str) != 7 or not date_to_str.isdigit():
        if date_to_str is not None: # Log only if it's not None but still invalid
            logger.debug(f"[_is_active_job] Invalid or non-standard date_to_str format: '{date_to_str}'")
        return False # Treat as inactive if date is missing or malformed
    
    try:
        roc_year = int(date_to_str[:3])
        month = int(date_to_str[3:5])
        day = int(date_to_str[5:7])
        
        gregorian_year = roc_year + 1911
        
        if not (1 <= month <= 12):
            logger.warning(f"[_is_active_job] Invalid month in date_to_str: '{date_to_str}' (Month: {month})")
            return False
        if not (1 <= day <= 31): 
            logger.warning(f"[_is_active_job] Invalid day in date_to_str: '{date_to_str}' (Day: {day})")
            return False
            
        date_to_obj = datetime(gregorian_year, month, day).date()
        today = datetime.today().date()
        
        is_active = date_to_obj >= today
        
        logger.debug(
            f"[_is_active_job] Checking job activity: "
            f"date_to_str='{date_to_str}' -> "
            f"ROC Year={roc_year}, Month={month}, Day={day} -> "
            f"Gregorian Year={gregorian_year} -> "
            f"date_to_obj={date_to_obj}, today={today}. Result: is_active={is_active}"
        )
        return is_active
    except ValueError as e: # Catches errors from int() conversion or invalid date for datetime (e.g. Feb 30)
        logger.warning(f"[_is_active_job] Date conversion ValueError for date_to_str='{date_to_str}'. Error: {e}")
        return False
    except Exception as e_generic: # Catch any other unexpected errors
        logger.error(f"[_is_active_job] Unexpected error processing date_to_str='{date_to_str}'. Error: {e_generic}", exc_info=True)
        return False

# --- Main Flex Message Creation Function ---

def create_job_flex_message_dict(all_job_listings: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not all_job_listings:
        logger.info("[create_job_flex_message_dict] Received empty or None all_job_listings.")
        return None # No data to process
    
    if len(all_job_listings) == 1 and "error_message" in all_job_listings[0]:
        error_msg = all_job_listings[0]['error_message']
        logger.error(f"[create_job_flex_message_dict] Error message received from DB service: {error_msg}")
        return { 
            "type": "text_message_special", # Custom type for webhook_router
            "text": error_msg
        }

    logger.info(f"[create_job_flex_message_dict] Received {len(all_job_listings)} potential listings from DB.")
    
    active_jobs = [job for job in all_job_listings if _is_active_job(job.get('date_to'))]
    
    if not active_jobs:
        logger.info("[create_job_flex_message_dict] No active job listings found after filtering by date_to.")
        return None

    logger.info(f"[create_job_flex_message_dict] Found {len(active_jobs)} active job listings after filtering.")
    
    active_jobs_to_display = active_jobs[:10] 
    
    bubbles = []
    first_bubble_logged = False 
    if active_jobs_to_display:
        for job_data in active_jobs_to_display:
            job_id = job_data.get('id') # 確保獲取 job_id
            org_name = job_data.get('org_name', 'N/A').strip()
            title = job_data.get('title', 'N/A').strip()
            sysnam_value = job_data.get('sysnam', '').strip() 
            rank_text = job_data.get('rank')
            
            work_place_type_value = job_data.get('work_place_type') # 主要地點來源

            date_from = job_data.get('date_from')
            date_to = job_data.get('date_to')
            
            # --- 構建 detail_url ---
            detail_url = None
            if job_id: # 首選 URL - 使用環境變數設定的網域
                import os
                site_domain = os.getenv("SITE_DOMAIN", "https://opendgpa.shibaalin.com").rstrip("/")
                detail_url = f"{site_domain}/job/{job_id}"
            
            if not detail_url: # 備援 1: 使用資料庫中的 view_url 或 url_link
                detail_url = job_data.get('view_url') or job_data.get('url_link')
            
            # 備援 2: 如果 job_id 存在但前述都失敗，使用舊的 DGPA 查詢連結 (這種情況較少發生)
            # 這一條通常在上面的 job_id 存在時就不會執行了，因為 detail_url 已被設定
            # 但保留以防萬一 job_id 存在，但上面的 `opendgpa.site` 邏輯因故未設定 detail_url
            if not detail_url and job_id:
                detail_url = f"https.dgpa.gov.tw/nds/P/Search_result.aspx?n=-1&sms=0&s={job_id}"

            if not detail_url: # 絕對備援: 通用 DGPA 網站
                 detail_url = "https.web3.dgpa.gov.tw/want03front/AP/WANTF00001.aspx"
            # --- End 構建 detail_url ---

            rank_display = _format_rank_display(rank_text)
            
            full_title = title
            if sysnam_value and sysnam_value.lower() not in title.lower():
                full_title = f"{title}｜{sysnam_value}"
            
            # 使用 work_place_type_value 進行地點格式化
            place_display = _format_place_for_display(work_place_type_value)


            bubble = {
                "type": "bubble",
                "size": "kilo",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "text", "text": org_name, "weight": "bold", "size": "lg",
                            "color": "#1E3A8A", "wrap": True, "margin": "none"
                        },
                        {
                            "type": "text", "text": full_title, "weight": "bold", "size": "md",
                            "wrap": True, "margin": "sm", "color": "#374151"
                        },
                        {"type": "separator", "margin": "md"},
                        {
                            "type": "box", "layout": "vertical", "spacing": "sm", "margin": "md",
                            "contents": [
                                {
                                    "type": "box", "layout": "baseline", "spacing": "sm",
                                    "contents": [
                                        {"type": "text", "text": "📈職等", "color": "#6B7280", "size": "xs", "flex": 3, "weight":"bold"},
                                        {"type": "text", "text": rank_display, "size": "xs", "flex": 7, "wrap": True, "color":"#1F2937"}
                                    ]
                                },
                                {
                                    "type": "box", "layout": "baseline", "spacing": "sm",
                                    "contents": [
                                        {"type": "text", "text": "📍地點", "color": "#6B7280", "size": "xs", "flex": 3, "weight":"bold"},
                                        {"type": "text", "text": place_display, "size": "xs", "flex": 7, "wrap": True, "color":"#1F2937"}
                                    ]
                                },
                                {
                                    "type": "box", "layout": "baseline", "spacing": "sm",
                                    "contents": [
                                        {"type": "text", "text": "🗓️期間", "color": "#6B7280", "size": "xs", "flex": 3, "weight":"bold"},
                                        {"type": "text", "text": f"{_format_roc_date_for_display(date_from)}～{_format_roc_date_for_display(date_to)}", 
                                         "size": "xs", "flex": 7, "wrap": True, "color":"#1F2937"}
                                    ]
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box", "layout": "vertical", "spacing": "sm", "contents": [
                        {"type": "button", "style": "link", "height": "sm", "color": "#2563EB",
                         "action": {"type": "uri", "label": "查看詳情", "uri": detail_url}}
                    ], "flex": 0
                }
            }
            bubbles.append(bubble)

            if not first_bubble_logged:
                try:
                    logger.debug(f"[create_job_flex_message_dict] First generated bubble structure: {json.dumps(bubble, ensure_ascii=False, indent=2)}")
                except Exception as e_dump_bubble:
                    logger.error(f"Error dumping first bubble: {e_dump_bubble}")
                first_bubble_logged = True
    
    if not bubbles:
        logger.info("[create_job_flex_message_dict] No valid bubbles were generated (e.g., active_jobs_to_display was empty).")
        return None 

    logger.info(f"[create_job_flex_message_dict] Generated {len(bubbles)} bubbles for Flex Message output.")
    
    alt_text = f"📋 為您找到{len(bubbles)}筆職缺資訊"
    if len(bubbles) == 1 and active_jobs_to_display:
        first_job_data = active_jobs_to_display[0]
        first_job_title = first_job_data.get('title', '職缺')
        first_job_org = first_job_data.get('org_name', '')
        alt_text_detail = f"{first_job_org} {first_job_title}".strip()
        alt_text = f"📋 為您找到「{alt_text_detail}」1筆職缺"


    if len(bubbles) == 1:
        return {
            "type": "flex",
            "altText": alt_text,
            "contents": bubbles[0]
        }
    else: 
        return {
            "type": "flex",
            "altText": alt_text,
            "contents": {"type": "carousel", "contents": bubbles} 
        }

# Legacy function - Kept for reference, but Flex Message is primary
def format_job_listings_for_line_reply(job_listings: List[Dict[str, Any]]) -> List[str]:
    logger.warning("[format_job_listings_for_line_reply] Legacy function called. Primary display is Flex Message.")
    if not job_listings:
        return ["抱歉，目前找不到符合您條件的職缺。"]
    if len(job_listings) == 1 and "error_message" in job_listings[0]:
        return [job_listings[0]["error_message"]]
    return ["已為您找到相關職缺，請參考上方卡片式訊息。若未顯示，請嘗試更新LINE版本或重新查詢。"]
