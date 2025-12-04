import re
from datetime import datetime

# -----------------------------
# 地點相關格式化
# -----------------------------

def format_place(place_str: str) -> str:
    """
    格式化工作地點字串：
    - 移除每個地點前的數字編號（如 '1-台北市' -> '台北市'）
    - 以逗號分隔地點
    - 若無資料則回傳 'N/A'
    """
    if not place_str:
        return "N/A"
    places = place_str.split(',')
    cleaned_places = [re.sub(r'^\s*\d+-', '', place.strip()) for place in places if place.strip()]
    return ', '.join(cleaned_places) if cleaned_places else "N/A"

def normalize_place(input_str: str) -> str:
    """
    正規化地點字串：將「台」轉為「臺」。
    """
    return input_str.replace('台', '臺')



# -----------------------------
# 日期相關格式化
# -----------------------------

def format_roc_date(date_str: str) -> str:
    """
    格式化民國日期字串：
    - 將 '1130425' 轉為 '113/04/25'
    - 若資料無效則回傳 'N/A'
    """
    if date_str and len(date_str) == 7:
        return f"{date_str[0:3]}/{date_str[3:5]}/{date_str[5:7]}"
    return date_str or "N/A"

def convert_to_gregorian_date(roc_date: str) -> str:
    """
    將中華民國日期 (YYYMMDD) 轉換為西元日期 (YYYY-MM-DD)
    """
    if not roc_date or len(roc_date) != 7 or not roc_date.isdigit():
        return ""
    try:
        roc_year = int(roc_date[:3])
        gregorian_year = roc_year + 1911
        return f"{gregorian_year}-{roc_date[3:5]}-{roc_date[5:7]}"
    except Exception:
        return ""

def convert_to_gregorian_date_iso(roc_date: str) -> str:
    """
    將中華民國日期 (YYYMMDD) 轉換為 ISO 8601 格式 (YYYY-MM-DD)
    用於結構化資料
    """
    if not roc_date or len(roc_date) != 7 or not roc_date.isdigit():
        return ""
    try:
        roc_year = int(roc_date[:3])
        gregorian_year = roc_year + 1911
        month = roc_date[3:5]
        day = roc_date[5:7]
        return f"{gregorian_year}-{month}-{day}"
    except Exception:
        return ""

# -----------------------------
# 職等相關格式化
# -----------------------------

def extract_rank_range(rank_text: str):
    """
    從職等文字中提取最低與最高職等數字。

    支援格式：
    - '委任第4職等待遇至委任第5職等' → (4, 5)
    - '薦任第6職等至薦任第7職等' → (6, 7)
    - '5等' → (5, 5)

    回傳：
    - (最小職等, 最大職等)
    - 若無法解析則回傳 (None, None)
    """
    if not rank_text:
        return None, None
    numbers = list(map(int, re.findall(r'(?:第\s*)?(\d+)(?=\s*(?:職|等))', rank_text)))
    if not numbers:
        return None, None
    return min(numbers), max(numbers)

def format_rank_display(rank_text: str) -> str:
    """
    將職等文字格式化成顯示字串。

    例：
    - '4等 - 5等'
    - '5等'
    - '無'
    """
    rmin, rmax = extract_rank_range(rank_text)
    if rmin is None or rmax is None:
        return "無"
    return f"{rmin}等" if rmin == rmax else f"{rmin}等 - {rmax}等"

def is_active_job(date_to: str) -> bool:
    """
    判斷職缺是否還在開缺期內（包含今天）。
    - date_to: 民國年月日 (7碼字串)，例如 '1140428'
    - 回傳 True 表示還有效，False 表示已過期
    """
    if not date_to or len(date_to) != 7:
        return False
    try:
        # 民國年轉西元年
        year = int(date_to[:3]) + 1911
        month = int(date_to[3:5])
        day = int(date_to[5:7])
        date_to_obj = datetime(year, month, day).date()  # 只取日期
        today = datetime.today().date()  # 只取日期
        return date_to_obj >= today
    except Exception:
        return False