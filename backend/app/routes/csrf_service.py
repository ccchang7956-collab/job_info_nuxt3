#csrf_service.py
import os
from fastapi import APIRouter, Depends
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel
from fastapi.responses import JSONResponse


class CsrfSettings(BaseModel):
    secret_key: str = os.getenv("CSRF_SECRET_KEY", "my_static_secret_key_for_testing_purposes")


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()


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
