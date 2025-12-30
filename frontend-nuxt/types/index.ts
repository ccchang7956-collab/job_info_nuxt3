export interface Comment {
    id: number
    user_id: number | null
    username: string
    initial: string
    message: string
    color: string
    created_at: string
    email: string | null
    job_all_data_id: number | null
    parent_id: number | null
    is_deleted: boolean
    children?: Comment[]
}

export interface CommentCreate {
    job_all_data_id: number
    username: string
    message: string
    color: string
    parent_id: number | null
    recaptcha_token: string
    email?: string
}

export interface CsrfTokenResponse {
    csrf_token: string
}

export interface Job {
    id: number
    org: string
    org_name?: string
    title: string
    sysnam: string
    rank: string
    rank_display: string
    place: string
    date_from: string
    date_to: string
    link: string
    history_count: number
    comment_count: number
    view_url?: string
    work_place_type?: string
    work_item?: string
    work_quality?: string
    work_address?: string
    contact_method?: string
    work_kind?: string
    person_kind?: string
    quota_regular?: number
    number_of?: number
    quota_backup?: string
    reserve_num?: string
    sort?: number
}

export interface JobListResponse {
    jobs: Job[]
    current_page: number
    per_page: number
    total_pages: number
    total_count: number
    page_range: number[]
    page_range_all: number[]
    today_date: string
    yesterday_date: string
}

export interface CommentListResponse {
    comments: Comment[]
    current_page: number
    per_page: number
    total_pages: number
    total_count: number
}

export interface Log {
    id: number
    action: string
    start_time: string
    end_time: string
    new_records: number
    updated_records: number
    status: string
    remarks: string
}

export interface LogListResponse {
    logs: Log[]
    actions: string[]
    total_pages: number
    total_count: number
    page_range: number[]
}

export interface ChartMonthOption {
    label: string
    value: string
}

// Search Params Interfaces
export interface JobSearchParams {
    page?: number
    org?: string
    title?: string
    sysnam?: string
    places?: string
    min_rank?: string
    max_rank?: string
    include_history?: boolean | string
    include_parttime?: boolean | string
}

export interface CommentSearchParams {
    page?: number
    search_org?: string
    search_title?: string
    search_sysnam?: string
    search_message?: string
    show_deleted?: boolean | string
}

export interface LogSearchParams {
    page?: number
    action?: string
}

export interface MostCommentedJob {
    id: number
    title: string
    org_name: string
    date_from: string
    date_to: string
    comment_count: number
}

export interface ChartDataResponse {
    month?: string
    month_options?: ChartMonthOption[]
    org_names?: string[]
    sys_names?: string[]
    dates?: string[]
    workplace_types?: string[]
    job_counts?: number[]
    most_commented_jobs?: MostCommentedJob[]
}

export interface JobDetailResponse {
    job: Job
    comments: Comment[]
    duplicates: Job[]
}

export interface Toast {
    id: number
    message: string
    type: 'success' | 'error' | 'info'
}
