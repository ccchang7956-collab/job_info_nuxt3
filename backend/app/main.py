# main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import logging
import sys
from pathlib import Path

# Import routes
from .api.search_sysnam import router as search_sysnam_router
from .utils.get_latest_update_date import get_latest_update_date
from .routes.job_details import router as job_details_router
from .routes.jobs import get_jobs_by_date_desc
from .routes.job_data_update_log import router as job_data_update_log_router
from .routes.job_openings_chart import router as job_openings_chart_router
from .routes.Job_Comments import router as Job_Comments_router
from .routes.comment_service import router as comment_router
from .routes.csrf_service import router as csrf_router
from .routes.about import router as about_router
from .routes.PrivacyPolicy_router import router as PrivacyPolicy_router
# from .routes.LINE_login import router as line_login_router
# from .routes.LINE_settings import router as line_settings_router
# from .routes.LINE_webhook import router as line_webhook
# from .LINE_AI.Line_ai_webhook_router import router as line_ai_bot_webhook_router
from .routes.metadata import router as metadata_router
from .routes.seo import router as seo_router

# ... existing imports ...



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
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

# Middleware 1: Inject update_date
@app.middleware("http")
async def add_update_date_to_request(request: Request, call_next):
    try:
        # Now awaiting the async function
        request.state.update_date = await get_latest_update_date()
    except Exception as e:
        logger.error(f"Error getting update date: {e}")
        request.state.update_date = "*/*/*"
    return await call_next(request)

# Middleware 2: Security headers
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
    allow_origins=["http://localhost", "http://127.0.0.1", "https://www.opendgpa.site", "https://opendgpa.site", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:5177"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
)

# Routes
app.get("/")(get_jobs_by_date_desc)
app.include_router(job_details_router)
app.include_router(search_sysnam_router)
app.include_router(job_data_update_log_router)
from app.routes.logs import router as logs_router
from app.routes.comments import router as comments_list_router

app.include_router(job_openings_chart_router)
app.include_router(logs_router)
app.include_router(comments_list_router)
app.include_router(Job_Comments_router)
app.include_router(comment_router, prefix="/comments", tags=["Comments"])
app.include_router(csrf_router, tags=["CSRF"])
app.include_router(about_router)
app.include_router(PrivacyPolicy_router)
# app.include_router(line_login_router)
# app.include_router(line_settings_router)
# app.include_router(line_webhook)
# app.include_router(line_ai_bot_webhook_router, prefix="/line_ai_bot", tags=["LINE AI Bot Service"])
app.include_router(metadata_router, prefix="/api/metadata", tags=["Metadata"])
app.include_router(seo_router)