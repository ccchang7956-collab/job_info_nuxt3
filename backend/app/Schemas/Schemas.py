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
    turnstile_token: str

    class Config:
        from_attributes = True



# 定義留言返回的資料結構 (單筆)
class CommentResponse(BaseModel):
    id: int
    user_id: Optional[int]
    username: str
    initial: str
    message: str
    color: str
    created_at: datetime
    email: Optional[str]
    job_all_data_id: Optional[int]
    parent_id: Optional[int]
    is_deleted: int

    class Config:
        from_attributes = True

# --- Job Schemas ---

class JobItem(BaseModel):
    id: int
    org: Optional[str] = None  # Frontend uses 'org'
    org_name: Optional[str] = None  # Pydantic schema field
    title: Optional[str] = None
    sysnam: Optional[str] = None
    rank: Optional[str] = None
    rank_display: Optional[str] = None  # Formatted rank for display
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    place: Optional[str] = None  # Frontend uses 'place' (formatted)
    work_place_type: Optional[str] = None  # Raw work_place_type
    work_item: Optional[str] = None
    view_url: Optional[str] = None
    announce_date: Optional[str] = None
    contact_method: Optional[str] = None
    history_count: int = 0
    comment_count: int = 0

    class Config:
        from_attributes = True

class JobListResponse(BaseModel):
    jobs: list[JobItem]
    current_page: int
    per_page: int
    total_pages: int
    page_range: list[int]
    page_range_all: list[int]
    total_count: int
    today_date: str
    yesterday_date: str

# --- Comment List Schemas ---

class CommentItem(BaseModel):
    comment_id: int
    message: str
    created_at: str # Formatted string from service
    job_all_data_id: int
    is_deleted: int
    deletion_reason: Optional[str]
    
    # Joined fields
    org_name: Optional[str]
    sysnam: Optional[str]
    title: Optional[str]
    date_from: Optional[str]
    date_to: Optional[str]
    rank: Optional[str]
    
    # User fields (dynamically added in service)
    user_id: Optional[int]
    username: Optional[str]
    initial: Optional[str]
    color: Optional[str]
    email: Optional[str]
    parent_id: Optional[int]

class CommentListResponse(BaseModel):
    comments: list[CommentItem]
    current_page: int
    per_page: int
    total_pages: int
    total_count: int
    sysnam_admin_list: list[str]
    sysnam_tech_list: list[str]

# --- Log Schemas ---

class LogItem(BaseModel):
    id: int
    action: str
    start_time: Optional[str]
    end_time: Optional[str]
    new_records: int
    updated_records: int
    status: Optional[str]
    remarks: Optional[str]

class LogListResponse(BaseModel):
    logs: list[LogItem]
    actions: list[str]
    current_page: int
    per_page: int
    total_pages: int
    total_count: int
    page_range: list[int]

# --- Job Detail Schemas ---

class CommentDetailItem(BaseModel):
    id: int
    username: str
    initial: str
    message: str
    color: str
    created_at: str
    parent_id: Optional[int]
    children: list['CommentDetailItem'] = []

class DuplicateJobItem(BaseModel):
    id: int
    org_name: Optional[str]
    title: Optional[str]
    date_from: Optional[str]
    date_to: Optional[str]

class JobDetailResponse(JobItem):
    comments: list[CommentDetailItem]
    formatted_duplicates: list[DuplicateJobItem]

# --- Chart Schemas ---

class MonthOption(BaseModel):
    value: str
    label: str

class BaseChartResponse(BaseModel):
    month: Optional[str] = None
    month_options: Optional[list[MonthOption]] = None

class ChartOrgResponse(BaseChartResponse):
    org_names: list[str]
    job_counts: list[int]

class ChartSysnamResponse(BaseChartResponse):
    sys_names: list[str]
    job_counts: list[int]

class ChartDailyResponse(BaseChartResponse):
    dates: list[str]
    job_counts: list[int]

class ChartPlaceResponse(BaseChartResponse):
    workplace_types: list[str]
    job_counts: list[int]

class MostCommentedJobItem(BaseModel):
    id: int
    org_name: Optional[str]
    title: Optional[str]
    date_from: Optional[str]
    date_to: Optional[str]
    comment_count: int

class ChartCommentsResponse(BaseModel):
    most_commented_jobs: list[MostCommentedJobItem]
