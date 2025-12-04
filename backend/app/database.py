import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# 從環境變數中讀取 DATABASE_URL，預設值為本地 MySQL
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root@localhost:3306/job_info")

# 創建資料庫引擎
engine = create_engine(DATABASE_URL)

# 創建 SessionLocal 類，用於生成會話
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 創建 Base 類，模型將繼承這個類
Base = declarative_base()

# 提供資料庫連線的依賴
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Async Database Support ---
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# 將 mysql+pymysql 替換為 mysql+aiomysql
ASYNC_DATABASE_URL = DATABASE_URL.replace("mysql+pymysql", "mysql+aiomysql").replace("localhost", "127.0.0.1")

async_engine = create_async_engine(ASYNC_DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db