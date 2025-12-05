import sys
import logging
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

# Logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:     %(asctime)s - %(name)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
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
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:3000",
    ] + Config.CORS_ORIGINS,
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
app.include_router(MetadataRouter.router, prefix="/api/metadata", tags=["Metadata"])
app.include_router(SeoRouter.router)