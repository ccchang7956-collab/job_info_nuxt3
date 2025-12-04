from fastapi import APIRouter, Depends
from fastapi_csrf_protect import CsrfProtect
from fastapi.responses import JSONResponse
from app.Services.CsrfService import get_csrf_config # Ensure config is loaded

router = APIRouter()

@router.get("/csrf_token")
def get_csrf_token(csrf_protect: CsrfProtect = Depends()):
    token = csrf_protect.generate_csrf()
    response = JSONResponse(content={"csrf_token": token})
    response.set_cookie(
        key=csrf_protect._cookie_key,
        value=token,
        httponly=True,
        secure=False,
        samesite="Lax"
    )
    return response
