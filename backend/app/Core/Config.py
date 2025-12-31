import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 取得資料庫檔案路徑 (backend/database/data/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "database" / "data" / "job_info.db"

class Config:
    # SQLite 資料庫連線
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
    ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", f"sqlite+aiosqlite:///{DB_PATH}")
    
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")
    GOOGLE_RECAPTCHA_SECRET_KEY = os.getenv("GOOGLE_RECAPTCHA_SECRET_KEY", "")

