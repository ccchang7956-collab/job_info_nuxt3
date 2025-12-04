from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .Config import Config

# 創建資料庫引擎
engine = create_engine(Config.DATABASE_URL)

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

async_engine = create_async_engine(
    Config.ASYNC_DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True
)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db