// Nuxt 3 auto-imports ref and onMounted
import type { CommentCreate, CsrfTokenResponse } from '../types'
import { useToast } from './useToast'

declare global {
    interface Window {
        turnstile?: {
            render: (container: string | HTMLElement, options: {
                sitekey: string
                callback?: (token: string) => void
                'expired-callback'?: () => void
                theme?: 'light' | 'dark' | 'auto'
            }) => string
            reset: (widgetId: string) => void
            getResponse: (widgetId: string) => string | undefined
        }
    }
}

export const useComments = (jobId: number, emitRefresh: () => void) => {
    const csrfToken = ref('')
    const submitting = ref(false)
    const error = ref<string | null>(null)
    const turnstileToken = ref<string>('')
    let widgetId: string | null = null
    const { addToast } = useToast()

    const colors = ['#ef4444', '#f97316', '#f59e0b', '#84cc16', '#10b981', '#06b6d4', '#3b82f6', '#6366f1', '#8b5cf6', '#d946ef', '#f43f5e'] as const
    const getRandomColor = (): string => colors[Math.floor(Math.random() * colors.length)] ?? '#3b82f6'

    const fetchCsrfToken = async () => {
        try {
            const response = await $fetch<CsrfTokenResponse>('/api/csrf_token')
            csrfToken.value = response.csrf_token
        } catch (err) {
            console.error('Failed to fetch CSRF token:', err)
        }
    }

    const renderTurnstile = (attempt = 0) => {
        const MAX_ATTEMPTS = 20
        if (attempt >= MAX_ATTEMPTS) {
            console.warn('Turnstile 載入超時，請重新整理頁面')
            return
        }
        if (window.turnstile && window.turnstile.render) {
            try {
                const container = document.getElementById('turnstile-container')
                if (container && !container.hasChildNodes()) {
                    const config = useRuntimeConfig()
                    widgetId = window.turnstile.render(container, {
                        sitekey: config.public.turnstileSiteKey as string,
                        callback: (token: string) => {
                            turnstileToken.value = token
                        },
                        'expired-callback': () => {
                            turnstileToken.value = ''
                        },
                        theme: 'auto'
                    })
                }
            } catch (e) {
                console.error('Turnstile render error:', e)
            }
        } else {
            setTimeout(() => renderTurnstile(attempt + 1), 500)
        }
    }

    const resetTurnstile = () => {
        if (widgetId !== null && window.turnstile) {
            window.turnstile.reset(widgetId)
            turnstileToken.value = ''
        }
    }

    const submitComment = async (username: string, message: string, replyToId: number | null) => {
        error.value = null

        if (!message.trim()) {
            error.value = '請填寫留言內容'
            return false
        }

        if (!turnstileToken.value) {
            error.value = '請完成機器人驗證'
            return false
        }

        submitting.value = true

        // 空白暱稱自動使用「匿名」
        const finalUsername = username.trim() || '匿名'

        try {
            const payload: CommentCreate = {
                job_all_data_id: jobId,
                username: finalUsername,
                message: message,
                color: getRandomColor(),
                parent_id: replyToId,
                turnstile_token: turnstileToken.value
            }

            await $fetch('/api/comments', {
                method: 'POST',
                body: payload,
                headers: {
                    'X-CSRF-Token': csrfToken.value
                }
            })

            resetTurnstile()
            emitRefresh()
            addToast('留言提交成功！', 'success')
            return true

        } catch (err: any) {
            console.error(err)
            error.value = err.data?.detail || '留言提交失敗，請稍後再試'
            return false
        } finally {
            submitting.value = false
        }
    }

    onMounted(() => {
        fetchCsrfToken()
        renderTurnstile()
    })

    return {
        submitting,
        error,
        submitComment
    }
}
