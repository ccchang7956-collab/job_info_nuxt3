import sys
import logging
import json
import uuid
import httpx
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.Core.Config import Config
from app.Utils.DateUtils import get_latest_update_date

# Import Routers
from app.Routers import (
    JobRouter,
    JobDetailRouter,
    SysnamRouter,
    LogRouter,
    ChartRouter,
    CommentRouter,
    JobCommentRouter,
    CsrfRouter,
    AboutRouter,
    PrivacyPolicyRouter,
    MetadataRouter,
    SeoRouter
)

# 結構化 JSON 日誌格式化器
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # 加入額外屬性 (request_id 等)
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "client_ip"):
            log_data["client_ip"] = record.client_ip
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)

# Logging setup - 使用結構化 JSON 日誌
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setFormatter(JsonFormatter())
logging.basicConfig(
    level=logging.INFO,
    handlers=[log_handler]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create HTTP client
    logger.info("Starting up application...")
    app.state.http_client = httpx.AsyncClient()
    yield
    # Shutdown: Close HTTP client
    logger.info("Shutting down application...")
    await app.state.http_client.aclose()

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)

# Static files
# Assuming static files are in backend/app/static. 
# Since we moved Main.py to backend/app/Main.py, parent is backend/app.
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

from fastapi.middleware.gzip import GZipMiddleware
from app.Core.Security import RateLimitMiddleware

# Middleware 1: Gzip Compression (High priority for performance)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Middleware 2: Rate Limiting
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

# Middleware 3: Inject update_date
@app.middleware("http")
async def add_update_date_to_request(request: Request, call_next):
    try:
        request.state.update_date = await get_latest_update_date()
    except Exception as e:
        logger.error(f"Error getting update date: {e}")
        request.state.update_date = "*/*/*"
    return await call_next(request)

# Middleware 4: Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    # Log request for audit trail
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Request: {request.method} {request.url.path} from {client_ip}")
    
    response = await call_next(request)
    
    # Security headers
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    # Content Security Policy (移除 unsafe-eval 提升安全性)
    csp = "; ".join([
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' https://www.google.com https://www.gstatic.com https://challenges.cloudflare.com",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
        "font-src 'self' https://fonts.gstatic.com",
        "img-src 'self' data: https:",
        "frame-src 'self' https://www.google.com https://challenges.cloudflare.com",
        "connect-src 'self' https://www.google.com"
    ])
    response.headers["Content-Security-Policy"] = csp
    
    # 快取控制
    if request.method == "GET" and response.status_code == 200:
        path = str(request.url.path)
        # API 路徑：不快取（每次驗證）
        if path == "/" or path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
        # 靜態資源：快取 1 小時
        else:
            response.headers["Cache-Control"] = "public, max-age=3600"
    
    return response

# CORS (localhost 僅在開發模式允許)
import os
dev_origins = []
if os.getenv("ENVIRONMENT", "production") == "development":
    dev_origins = ["http://localhost", "http://127.0.0.1", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=dev_origins + Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
)

# Include Routers
app.include_router(JobRouter.router)
app.include_router(JobDetailRouter.router)
app.include_router(SysnamRouter.router)
app.include_router(LogRouter.router)
app.include_router(ChartRouter.router)
app.include_router(CommentRouter.router, prefix="/comments", tags=["Comments"])
app.include_router(JobCommentRouter.router)
app.include_router(CsrfRouter.router, tags=["CSRF"])
app.include_router(AboutRouter.router)
app.include_router(PrivacyPolicyRouter.router)
app.include_router(MetadataRouter.router, prefix="/metadata", tags=["Metadata"])
app.include_router(SeoRouter.router)