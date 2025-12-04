from fastapi_csrf_protect import CsrfProtect
from fastapi import Request
from pydantic import BaseModel

csrf = CsrfProtect()
# Mock config
class Config(BaseModel):
    secret_key: str = "secret"
csrf.load_config(Config())

token = csrf.generate_csrf()
print(f"Token: {token}")

# Check validate_csrf signature/usage
import inspect
print(f"validate_csrf signature: {inspect.signature(csrf.validate_csrf)}")
