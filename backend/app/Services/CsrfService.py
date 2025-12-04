import os
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel

class CsrfSettings(BaseModel):
    secret_key: str = os.getenv("CSRF_SECRET_KEY", "my_static_secret_key_for_testing_purposes")

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()
