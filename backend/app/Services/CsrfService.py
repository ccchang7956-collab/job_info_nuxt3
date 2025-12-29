import os
import secrets
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel, Field

def get_csrf_secret():
    key = os.getenv("CSRF_SECRET_KEY")
    # Strict check: if missing or default, generate random
    if not key or key == "my_static_secret_key_for_testing_purposes":
        print("WARNING: CSRF_SECRET_KEY not set or is default! Using a temporary random key. Sessions will be invalidated on restart.")
        return secrets.token_hex(32)
    return key

class CsrfSettings(BaseModel):
    secret_key: str = Field(default_factory=get_csrf_secret)

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()
