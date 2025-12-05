from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# 定義留言建立的請求資料結構
class CommentCreate(BaseModel):
    user_id: Optional[int] = None
    username: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=500)
    color: str = Field(..., pattern=r'^#[0-9a-fA-F]{6}$')
    email: Optional[str] = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    job_all_data_id: Optional[int] = None
    parent_id: Optional[int] = None
    recaptcha_token: str

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}
