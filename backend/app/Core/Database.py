from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from .Config import Config

# 創建資料庫引擎 (SQLite 需要 check_same_thread=False)
engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})

# SQLite 優化設定 (同步引擎)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("PRAGMA cache_size=-64000;")  # 64MB cache
    cursor.execute("PRAGMA temp_store=MEMORY;")
    cursor.close()

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
    connect_args={"check_same_thread": False},  # SQLite 需要此設定
    echo=False
)

# SQLite 優化設定 (非同步引擎)
@event.listens_for(async_engine.sync_engine, "connect")
def set_sqlite_pragma_async(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("PRAGMA cache_size=-64000;")
    cursor.execute("PRAGMA temp_store=MEMORY;")
    cursor.close()

AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        except Exception:
            await db.rollback()
            raise