import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root@localhost:3306/job_info")
    ASYNC_DATABASE_URL = DATABASE_URL.replace("mysql+pymysql", "mysql+aiomysql").replace("localhost", "127.0.0.1")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")
