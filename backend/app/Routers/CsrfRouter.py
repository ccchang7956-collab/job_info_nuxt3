from fastapi import APIRouter
from app.Services.CsrfService import get_csrf_token_response

router = APIRouter()


@router.get("/csrf_token")
def get_csrf_token():
    """Generate and return a CSRF token."""
    return get_csrf_token_response()
