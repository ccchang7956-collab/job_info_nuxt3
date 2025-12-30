import type {
    JobListResponse,
    CommentListResponse,
    LogListResponse,
    JobSearchParams,
    CommentSearchParams,
    LogSearchParams,
    JobDetailResponse
} from '@/types'

// Retry 配置
const RETRY_CONFIG = {
    maxRetries: 3,
    retryDelay: 1000, // 毫秒
    retryableStatuses: [408, 429, 500, 502, 503, 504]
}

// 延遲函式
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// 帶有 retry 機制的 fetch 包裝
async function fetchWithRetry<T>(
    url: string,
    options: Parameters<typeof $fetch>[1] = {},
    signal?: AbortSignal
): Promise<T> {
    let lastError: Error | null = null

    for (let attempt = 0; attempt <= RETRY_CONFIG.maxRetries; attempt++) {
        try {
            // 檢查是否已取消
            if (signal?.aborted) {
                throw new Error('請求已被取消')
            }

            return await $fetch<T>(url, {
                ...options,
                signal
            })
        } catch (error: any) {
            lastError = error

            // 檢查是否為可重試的錯誤
            const status = error?.response?.status || error?.status
            const isRetryable = RETRY_CONFIG.retryableStatuses.includes(status) ||
                error?.name === 'FetchError' ||
                error?.message?.includes('network')

            // 如果已達最大重試次數或不可重試，則拋出錯誤
            if (attempt >= RETRY_CONFIG.maxRetries || !isRetryable) {
                throw error
            }

            // 指數退避延遲
            const backoffDelay = RETRY_CONFIG.retryDelay * Math.pow(2, attempt)
            console.warn(`API 請求失敗，${backoffDelay}ms 後重試 (${attempt + 1}/${RETRY_CONFIG.maxRetries})`, error)
            await delay(backoffDelay)
        }
    }

    throw lastError
}

export const useJobApi = () => {
    // 用於追蹤和取消進行中的請求
    const abortControllers = new Map<string, AbortController>()

    // 建立可取消的請求
    const createCancellableRequest = <T>(
        key: string,
        requestFn: (signal: AbortSignal) => Promise<T>
    ): Promise<T> => {
        // 取消先前的同類型請求
        const existingController = abortControllers.get(key)
        if (existingController) {
            existingController.abort()
        }

        // 建立新的 AbortController
        const controller = new AbortController()
        abortControllers.set(key, controller)

        return requestFn(controller.signal).finally(() => {
            // 請求完成後清理
            if (abortControllers.get(key) === controller) {
                abortControllers.delete(key)
            }
        })
    }

    // 取消特定類型的請求
    const cancelRequest = (key: string) => {
        const controller = abortControllers.get(key)
        if (controller) {
            controller.abort()
            abortControllers.delete(key)
        }
    }

    // 取消所有進行中的請求
    const cancelAllRequests = () => {
        abortControllers.forEach(controller => controller.abort())
        abortControllers.clear()
    }

    // Client-side Fetchers with retry and cancellation
    const fetchJobs = (params: JobSearchParams): Promise<JobListResponse> => {
        return createCancellableRequest('jobs', (signal) =>
            fetchWithRetry<JobListResponse>('/api/jobs', { params }, signal)
        )
    }

    const fetchComments = (params: CommentSearchParams): Promise<CommentListResponse> => {
        return createCancellableRequest('comments', (signal) =>
            fetchWithRetry<CommentListResponse>('/api/comments/list', { params }, signal)
        )
    }

    const fetchJobDetail = (id: number): Promise<JobDetailResponse> => {
        return createCancellableRequest(`job-${id}`, (signal) =>
            fetchWithRetry<JobDetailResponse>(`/api/jobs/${id}`, {}, signal)
        )
    }

    const fetchLogs = (params: LogSearchParams): Promise<LogListResponse> => {
        return createCancellableRequest('logs', (signal) =>
            fetchWithRetry<LogListResponse>('/api/logs', { params }, signal)
        )
    }

    return {
        fetchJobs,
        fetchComments,
        fetchJobDetail,
        fetchLogs,
        cancelRequest,
        cancelAllRequests
    }
}
