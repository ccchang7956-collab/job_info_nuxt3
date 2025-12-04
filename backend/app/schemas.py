from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# 定義留言建立的請求資料結構
class CommentCreate(BaseModel):
    user_id: Optional[int] = None  # 設為可選
    username: str
    message: str
    color: str
    email: Optional[str] = None
    job_all_data_id: Optional[int] = None  # 改為 job_all_data_id
    parent_id: Optional[int] = None
    recaptcha_token: str  # 添加此屬性
    
    class Config:
        orm_mode = True  # Pydantic V1 uses orm_mode
    

# 定義留言返回的資料結構
class CommentResponse(BaseModel):
    id: int
    user_id: Optional[int]  # 設為可選
    username: str
    initial: str
    message: str
    color: str
    created_at: datetime
    email: Optional[str]
    job_all_data_id: Optional[int]  # 改為 job_all_data_id
    parent_id: Optional[int]
    is_deleted: bool

    class Config:
        orm_mode = True  # Pydantic V1 uses orm_mode
