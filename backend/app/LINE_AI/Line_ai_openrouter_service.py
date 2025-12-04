# LINE_AI/Line_ai_openrouter_service.py
import os
import json
import logging
import httpx
import re
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any

load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_CHAT_MODEL = os.getenv("OPENROUTER_CHAT_MODEL", "google/gemini-2.0-flash-exp:free")
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL")
OPENROUTER_SITE_NAME = os.getenv("OPENROUTER_SITE_NAME", "LINE-AI-Job-Bot")

# --- START OF JOB SERIES AND LOCATION LISTS ---
VALID_JOB_SERIES = [
    # 行政職系
    "綜合行政", "人事行政", "經建行政", "會計審計", "文教行政", "社勞行政",
    "地政", "衛生行政", "法制", "交通行政", "社會工作", "司法行政",
    "廉政", "統計", "環保行政", "海巡行政", "新聞傳播",
    # 技術職系
    "土木工程", "電機工程", "資訊處理", "財稅金融", "農業技術", "測量製圖",
    "建築工程", "交通技術", "獸醫", "衛生技術", "機械工程", "都市計畫",
    "動物技術", "景觀設計", "環資技術", "工業工程", "自然保育",
    "圖書史料檔案", "地質礦治", "職業安全衛生", "醫學工程", "林業技術",
    "消防技術", "技藝"
]

VALID_LOCATIONS_TAIWAN = [ # 這是給 AI 參考的台灣主要縣市，用於引導，AI 仍需從使用者輸入提取
    "臺北市", "新北市", "基隆市", "桃園市", "新竹縣", "新竹市", "苗栗縣",
    "臺中市", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "嘉義市", "臺南市",
    "高雄市", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"
]

# --- START OF REGIONAL EXPANSION MAPPING ---
# This mapping helps the AI understand regional terms and expand them.
REGIONAL_EXPANSIONS = {
    # General Major Regions
    "北部": ["臺北市", "新北市", "基隆市", "桃園市", "新竹縣", "新竹市", "苗栗縣"],
    "中部": ["臺中市", "彰化縣", "南投縣"],  # Per user: 中部 often means 中彰投
    "南部": ["雲林縣", "嘉義縣", "嘉義市", "臺南市", "高雄市", "屏東縣"], # Covers 雲嘉南 and 高屏
    "東部": ["宜蘭縣", "花蓮縣", "臺東縣"],
    "離島": ["澎湖縣", "金門縣", "連江縣"],

    # Common Synonyms for Major Regions
    "北臺灣": ["臺北市", "新北市", "基隆市", "桃園市", "新竹縣", "新竹市", "苗栗縣"],
    "中臺灣": ["臺中市", "彰化縣", "南投縣"],
    "南臺灣": ["雲林縣", "嘉義縣", "嘉義市", "臺南市", "高雄市", "屏東縣"],
    "東臺灣": ["宜蘭縣", "花蓮縣", "臺東縣"],

    # Sub-regions and Common Groupings
    "北北基": ["臺北市", "新北市", "基隆市"],
    "北北基地區": ["臺北市", "新北市", "基隆市"],
    "北北基桃": ["臺北市", "新北市", "基隆市", "桃園市"],
    "雙北": ["臺北市", "新北市"], # Common term for Taipei and New Taipei
    "北基": ["臺北市", "基隆市"],

    "桃竹苗": ["桃園市", "新竹縣", "新竹市", "苗栗縣"],
    "桃竹苗地區": ["桃園市", "新竹縣", "新竹市", "苗栗縣"],
    "竹苗": ["新竹縣", "新竹市", "苗栗縣"],
    "竹科地區": ["新竹市", "新竹縣"], # For "竹科" often implying the surrounding cities for job search

    "中彰投": ["臺中市", "彰化縣", "南投縣"],
    "中彰投地區": ["臺中市", "彰化縣", "南投縣"],

    "雲嘉南": ["雲林縣", "嘉義縣", "嘉義市", "臺南市"],
    "雲嘉南地區": ["雲林縣", "嘉義縣", "嘉義市", "臺南市"],
    "嘉南": ["嘉義縣", "嘉義市", "臺南市"],

    "高屏": ["高雄市", "屏東縣"],
    "高屏地區": ["高雄市", "屏東縣"],
    "高高屏": ["高雄市", "屏東縣"], # Historically relevant, now essentially same as 高屏

    "宜花東": ["宜蘭縣", "花蓮縣", "臺東縣"],
    "宜花東地區": ["宜蘭縣", "花蓮縣", "臺東縣"],

    "澎金馬": ["澎湖縣", "金門縣", "連江縣"] # Common term for the main outlying islands
}
# --- END OF REGIONAL EXPANSION MAPPING ---
# --- END OF JOB SERIES AND LOCATION LISTS ---

# --- START OF HELPER FUNCTION FOR LOCATION NORMALIZATION ---
def _normalize_locations_in_list(locations: Optional[List[str]]) -> Optional[List[str]]:
    """
    Normalizes '台' to '臺' for each location string in a list.
    Ensures locations end with '市' or '縣' if they are major administrative divisions.
    Example: "台北" -> "臺北市", "台中" -> "臺中市", "台南市" -> "臺南市"
    """
    if not locations:
        return None
    
    normalized_locations = []
    taiwan_admin_divisions_prefixes = {
        "臺北": "臺北市", "新北": "新北市", "基隆": "基隆市", "桃園": "桃園市",
        "新竹": "新竹市", 
        "新竹縣": "新竹縣", 
        "苗栗": "苗栗縣", "臺中": "臺中市", "彰化": "彰化縣", "南投": "南投縣",
        "雲林": "雲林縣", "嘉義": "嘉義市", 
        "嘉義縣": "嘉義縣", 
        "臺南": "臺南市", "高雄": "高雄市", "屏東": "屏東縣", "宜蘭": "宜蘭縣",
        "花蓮": "花蓮縣", "臺東": "臺東縣", "澎湖": "澎湖縣", "金門": "金門縣",
        "連江": "連江縣"
    }

    unique_locations = []
    seen_locations = set()

    for loc in locations:
        normalized_loc = loc.replace("台", "臺").strip()

        # Attempt to match with full names first (e.g. if AI returns "新竹縣" correctly)
        if normalized_loc in taiwan_admin_divisions_prefixes.values(): # e.g. "臺北市" is a value
            final_loc = normalized_loc
        # Then attempt to match prefixes (e.g. "臺北" -> "臺北市")
        elif normalized_loc in taiwan_admin_divisions_prefixes:
            final_loc = taiwan_admin_divisions_prefixes[normalized_loc]
        # Handle cases where it already has a suffix but might need '台' -> '臺' normalization (e.g. "台北市")
        elif (normalized_loc.endswith("市") or normalized_loc.endswith("縣")) and \
             taiwan_admin_divisions_prefixes.get(normalized_loc[:-1]):
             final_loc = taiwan_admin_divisions_prefixes[normalized_loc[:-1]] # e.g. "臺北" from "臺北市" then map
        else: # If not a known prefix or full name, keep as is (e.g. "臺北市中山區", or unexpected AI output)
            final_loc = normalized_loc
        
        if final_loc and final_loc not in seen_locations:
            unique_locations.append(final_loc)
            seen_locations.add(final_loc)
                
    return unique_locations if unique_locations else None
# --- END OF HELPER FUNCTION FOR LOCATION NORMALIZATION ---

def _generate_regional_mapping_prompt_section_text() -> str:
    """Generates the regional mapping part of the system prompt."""
    prompt_lines = ["以下是一些常見的區域性詞彙及其對應的縣市列表，請你參考並進行擴展："]
    for region_term, cities in REGIONAL_EXPANSIONS.items():
        city_list_str = "、".join(f"「{city}」" for city in cities)
        prompt_lines.append(f"  - 若使用者提到「{region_term}」，請將其視為包含 {city_list_str}。")
    return "\n".join(prompt_lines)

def _parse_ai_response(ai_message_content: str) -> Dict[str, Any]:
    try:
        return json.loads(ai_message_content)
    except json.JSONDecodeError:
        logger.warning(f"AI response was not pure JSON: {ai_message_content}. Attempting to extract JSON block.")
        match = re.search(r"\{.*\}", ai_message_content, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e_inner:
                logger.error(f"Could not parse extracted JSON from AI response: {e_inner}. Raw: {ai_message_content}")
                return {}
        else:
            logger.error(f"Could not find JSON block in AI response: {ai_message_content}")
            return {}

async def get_job_search_criteria_from_ai(user_text: str, client: Optional[httpx.AsyncClient] = None) -> Dict[str, Optional[List[str]]]:
    default_criteria: Dict[str, Optional[List[str]]] = {"job_series": None, "location": None}
    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY not configured.")
        return default_criteria

    job_series_list_for_prompt = "、".join(VALID_JOB_SERIES)
    regional_mapping_text_for_prompt = _generate_regional_mapping_prompt_section_text()
    valid_locations_list_for_prompt = "、".join(VALID_LOCATIONS_TAIWAN)


    prompt_system = f"""
你是協助查詢台灣公家機關與國營事業職缺的助手。
請從使用者問題中，提取出「職系」(job_series) 和「工作地點縣市」(location)。
這兩個欄位都可能包含多個值。

「職系」(job_series) 指的是專業分類。請從以下提供的有效職系列表中識別並提取使用者提到的所有職系，並以**字串陣列**回傳。
有效職系列表參考：{job_series_list_for_prompt}。
如果使用者提到的詞語接近但不完全匹配列表中的職系，請嘗試匹配到最相似的有效職系。例如，若使用者說「行政」，通常指的是「綜合行政」。若使用者說「資訊」，指的是「資訊處理」。若說「會計」，指的是「會計審計」。
若未提及任何相關職系，則 job_series 設為 null。

「工作地點縣市」(location) 請提取或推斷出所有相關的台灣縣市名稱，並以**字串陣列**回傳。
- 首先，將使用者輸入的地名中的「台」統一轉換為「臺」。例如，若使用者說「台中」，視為「臺中」。
- 其次，參考以下區域性詞彙與其對應的縣市列表。若使用者提到這些區域詞彙，請將其擴展為相應的完整縣市列表：
{regional_mapping_text_for_prompt}
- 使用者可能同時提及區域詞彙、特定縣市名稱（例如：台北市、新北市、桃園市、台中市、高雄市等），或兩者皆有。你的目標是產生一個包含所有提及或暗示的縣市的最終列表。
- 合併規則：
    - 如果使用者明確提及特定縣市，則這些縣市必須包含在最終列表中。
    - 如果使用者提及區域詞彙，則該區域對應的所有縣市都必須包含在最終列表中。
    - 將所有這樣識別出的縣市（來自直接提及和區域擴展）合併成一個列表。
- 格式化最終列表：
    - 列表中的每個縣市名稱都應使用「臺」字（例如「臺北市」而非「台北市」）。
    - 盡可能為縣市名稱補上後綴「市」或「縣」（例如，若推斷出「臺北」，則輸出「臺北市」；「新竹」則優先輸出「新竹市」，除非上下文明確指向「新竹縣」）。參考此列表確認主要縣市的完整名稱：{valid_locations_list_for_prompt}。
    - 確保最終列表中的縣市名稱**沒有重複**。
- 若根據上述規則無法提取或推斷出任何具體的縣市（例如，使用者僅說「我想找工作」或「地點不拘」），則 location 設為 null。

如果使用者沒有明確提到某個項目的任何內容，則該項目在 JSON 中應為 null。
請以 JSON 格式回傳，必須包含 "job_series" 和 "location" 兩個鍵。這兩個鍵的值可以是**字串陣列** (e.g., ["綜合行政", "資訊處理"]) 或 null。不要包含任何 markdown 語法或解釋，直接回傳純粹的 JSON 物件。

範例使用者輸入與你的輸出：
1. 使用者：「我想找台北的綜合行政」
   你輸出：{{"job_series": ["綜合行政"], "location": ["臺北市"]}}
2. 使用者：「有沒有土木工程的缺，在高雄或台南」
   你輸出：{{"job_series": ["土木工程"], "location": ["高雄市", "臺南市"]}}
3. 使用者：「幫我找資訊處理或會計的」
   你輸出：{{"job_series": ["資訊處理", "會計審計"], "location": null}}
4. 使用者：「宜蘭或花蓮有什麼職缺嗎」
   你輸出：{{"job_series": null, "location": ["宜蘭縣", "花蓮縣"]}}
5. 使用者：「我想找電力的，地點不拘」
   你輸出：{{"job_series": ["電機工程"], "location": null}}
6. 使用者：「土木跟建築，台中或彰化」
   你輸出：{{"job_series": ["土木工程", "建築工程"], "location": ["臺中市", "彰化縣"]}}
7. 使用者：「我想找工作」
   你輸出：{{"job_series": null, "location": null}}
8. 使用者：「屏東的社工缺」
    你輸出：{{"job_series": ["社會工作"], "location": ["屏東縣"]}}
9. 使用者：「台北資訊」
    你輸出：{{"job_series": ["資訊處理"], "location": ["臺北市"]}}
10. 使用者：「我想找中部的行政工作」
    你輸出：{{"job_series": ["綜合行政"], "location": ["臺中市", "彰化縣", "南投縣"]}}
11. 使用者：「北北基的資訊缺」
    你輸出：{{"job_series": ["資訊處理"], "location": ["臺北市", "新北市", "基隆市"]}}
12. 使用者：「我想找南部的土木，或是在桃園也可以」
    你輸出：{{"job_series": ["土木工程"], "location": ["雲林縣", "嘉義縣", "嘉義市", "臺南市", "高雄市", "屏東縣", "桃園市"]}}
13. 使用者：「東部或離島的工作」
    你輸出：{{"job_series": null, "location": ["宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"]}}
14. 使用者：「有沒有竹科地區的缺」
    你輸出：{{"job_series": null, "location": ["新竹市", "新竹縣"]}}
15. 使用者：「我想找工作，中彰投地區」
    你輸出：{{"job_series": null, "location": ["臺中市", "彰化縣", "南投縣"]}}
"""

    messages = [
        {"role": "system", "content": prompt_system},
        {"role": "user", "content": user_text}
    ]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    if OPENROUTER_SITE_URL: headers["HTTP-Referer"] = OPENROUTER_SITE_URL
    if OPENROUTER_SITE_NAME: headers["X-Title"] = OPENROUTER_SITE_NAME

    payload = {
        "model": OPENROUTER_CHAT_MODEL,
        "messages": messages,
        "response_format": {"type": "json_object"}
    }

    try:
        if client:
            response = await client.post(
                f"{OPENROUTER_API_BASE}/chat/completions",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            api_response_json = response.json()
            ai_message_content = api_response_json.get("choices", [{}])[0].get("message", {}).get("content")
            
            if not ai_message_content:
                logger.warning("OpenRouter returned empty content.")
                return default_criteria
            
            extracted_criteria_raw = _parse_ai_response(ai_message_content)
            
        else:
            async with httpx.AsyncClient() as local_client:
                response = await local_client.post(
                    f"{OPENROUTER_API_BASE}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                api_response_json = response.json()
                ai_message_content = api_response_json.get("choices", [{}])[0].get("message", {}).get("content")

                if not ai_message_content:
                    logger.warning("OpenRouter returned empty content.")
                    return default_criteria
                
                extracted_criteria_raw = _parse_ai_response(ai_message_content)
        
        final_criteria: Dict[str, Optional[List[str]]] = {}
        for key in ["job_series", "location"]:
            value = extracted_criteria_raw.get(key)
            
            if value is None:
                final_criteria[key] = None
            elif isinstance(value, str):
                stripped_value = value.strip()
                if stripped_value:
                    if key == "job_series" and stripped_value not in VALID_JOB_SERIES:
                         logger.warning(f"AI returned job_series '{stripped_value}' not in predefined list. Accepting it.")
                    final_criteria[key] = [stripped_value]
                else:
                    final_criteria[key] = None
            elif isinstance(value, list):
                processed_list = []
                for item in value:
                    if isinstance(item, str):
                        stripped_item = str(item).strip()
                        if stripped_item:
                            if key == "job_series" and stripped_item not in VALID_JOB_SERIES:
                                logger.warning(f"AI returned job_series '{stripped_item}' in list not in predefined list. Accepting it.")
                            processed_list.append(stripped_item)
                
                if processed_list:
                    # Ensure uniqueness, especially for locations if AI doesn't perfectly dedup
                    final_criteria[key] = list(dict.fromkeys(processed_list)) 
                else:
                    final_criteria[key] = None
            else:
                logger.warning(f"AI returned unexpected type for {key}: {value} (type: {type(value)}). Setting to None.")
                final_criteria[key] = None
        
        if "job_series" not in final_criteria:
             final_criteria["job_series"] = None
        if "location" not in final_criteria:
             final_criteria["location"] = None

        # --- APPLY NORMALIZATION TO LOCATION LIST AFTER AI EXTRACTION ---
        if final_criteria.get("location"):
            logger.debug(f"Original locations from AI: {final_criteria['location']}")
            final_criteria["location"] = _normalize_locations_in_list(final_criteria["location"])
            logger.debug(f"Normalized locations after _normalize_locations_in_list: {final_criteria['location']}")
        # --- END OF NORMALIZATION ---

        logger.info(f"OpenRouter AI extracted criteria (after location normalization): {final_criteria}")
        return final_criteria

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error calling OpenRouter: {e.response.status_code} - {e.response.text}")
        return default_criteria
    except httpx.RequestError as e:
        logger.error(f"Request error calling OpenRouter: {e}")
        return default_criteria
    except json.JSONDecodeError as e:
        response_text = response.text if 'response' in locals() else 'N/A'
        logger.error(f"Error decoding JSON response structure from OpenRouter: {e}. Response text: {response_text}")
        return default_criteria
    except Exception as e:
        logger.error(f"Unexpected error calling OpenRouter AI: {e}", exc_info=True)
        return default_criteria