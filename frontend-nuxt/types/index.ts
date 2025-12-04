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
