import type {
    JobListResponse,
    CommentListResponse,
    LogListResponse,
    JobSearchParams,
    CommentSearchParams,
    LogSearchParams,
    JobDetailResponse
} from '@/types'

export const useJobApi = () => {
    // Client-side Fetchers
    const fetchJobs = async (params: JobSearchParams): Promise<JobListResponse> => {
        return await $fetch<JobListResponse>('/api/jobs', { params })
    }

    const fetchComments = async (params: CommentSearchParams): Promise<CommentListResponse> => {
        return await $fetch<CommentListResponse>('/api/comments/list', { params })
    }

    const fetchJobDetail = async (id: number) => {
        return await $fetch<JobDetailResponse>(`/api/jobs/${id}`)
    }

    const fetchLogs = async (params: LogSearchParams): Promise<LogListResponse> => {
        return await $fetch<LogListResponse>('/api/logs', { params })
    }

    return {
        fetchJobs,
        fetchComments,
        fetchJobDetail,
        fetchLogs
    }
}
