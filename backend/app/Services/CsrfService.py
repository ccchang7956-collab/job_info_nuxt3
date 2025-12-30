import os
import secrets
import hmac
import hashlib
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

# Get or generate CSRF secret
def get_csrf_secret():
    key = os.getenv("CSRF_SECRET_KEY")
    if not key or key == "my_static_secret_key_for_testing_purposes":
        print("WARNING: CSRF_SECRET_KEY not set! Using a temporary random key.")
        key = secrets.token_hex(32)
    return key

CSRF_SECRET = get_csrf_secret()
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"


def generate_csrf_token() -> str:
    """Generate a new CSRF token."""
    random_bytes = secrets.token_hex(32)
    signature = hmac.new(
        CSRF_SECRET.encode(), 
        random_bytes.encode(), 
        hashlib.sha256
    ).hexdigest()
    return f"{random_bytes}.{signature}"


def validate_csrf_token(token: str) -> bool:
    """Validate a CSRF token."""
    if not token or "." not in token:
        return False
    try:
        random_bytes, signature = token.rsplit(".", 1)
        expected_signature = hmac.new(
            CSRF_SECRET.encode(), 
            random_bytes.encode(), 
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)
    except Exception:
        return False


async def verify_csrf(request: Request):
    """Dependency to verify CSRF token for state-changing requests."""
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        header_token = request.headers.get(CSRF_HEADER_NAME)
        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        
        # Both must be present and match
        if not header_token or not cookie_token:
            raise HTTPException(status_code=403, detail="CSRF token missing")
        
        if header_token != cookie_token:
            raise HTTPException(status_code=403, detail="CSRF token mismatch")
        
        if not validate_csrf_token(header_token):
            raise HTTPException(status_code=403, detail="Invalid CSRF token")
    
    return True


def get_csrf_token_response() -> JSONResponse:
    """Generate a response with CSRF token in both body and cookie."""
    token = generate_csrf_token()
    response = JSONResponse(content={"csrf_token": token})
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        httponly=False,  # Frontend needs to read it
        secure=False,    # Allow HTTP for dev
        samesite="lax",
        max_age=3600     # 1 hour
    )
    return response
