import { ref, onMounted } from 'vue'
import type { CommentCreate, CsrfTokenResponse } from '../types'
import { useToast } from './useToast'

export const useComments = (jobId: number, emitRefresh: () => void) => {
    const csrfToken = ref('')
    const submitting = ref(false)
    const error = ref<string | null>(null)
    let widgetId: number | null = null
    const { addToast } = useToast()

    const colors = ['#ef4444', '#f97316', '#f59e0b', '#84cc16', '#10b981', '#06b6d4', '#3b82f6', '#6366f1', '#8b5cf6', '#d946ef', '#f43f5e']
    const getRandomColor = () => colors[Math.floor(Math.random() * colors.length)]

    const fetchCsrfToken = async () => {
        try {
            const response = await $fetch<CsrfTokenResponse>('/api/csrf_token')
            csrfToken.value = response.csrf_token
        } catch (err) {
            console.error('Failed to fetch CSRF token:', err)
        }
    }

    const renderRecaptcha = () => {
        if (window.grecaptcha && window.grecaptcha.render) {
            try {
                const container = document.getElementById('recaptcha-container')
                if (container && !container.hasChildNodes()) {
                    const config = useRuntimeConfig()
                    widgetId = window.grecaptcha.render('recaptcha-container', {
                        'sitekey': config.public.recaptchaSiteKey as string
                    })
                }
            } catch (e) {
                console.error('Recaptcha render error:', e)
            }
        } else {
            setTimeout(renderRecaptcha, 500)
        }
    }

    const resetRecaptcha = () => {
        if (widgetId !== null && window.grecaptcha) {
            window.grecaptcha.reset(widgetId)
        }
    }

    const submitComment = async (username: string, message: string, replyToId: number | null) => {
        error.value = null

        if (!username.trim() || !message.trim()) {
            error.value = '請填寫暱稱和留言內容'
            return false
        }

        if (!window.grecaptcha) {
            error.value = 'reCAPTCHA 尚未載入，請稍後再試'
            return false
        }

        const recaptchaToken = window.grecaptcha.getResponse(widgetId)
        if (!recaptchaToken) {
            error.value = '請完成機器人驗證'
            return false
        }

        submitting.value = true

        try {
            const payload: CommentCreate = {
                job_all_data_id: jobId,
                username: username,
                message: message,
                color: getRandomColor(),
                parent_id: replyToId,
                recaptcha_token: recaptchaToken
            }

            await $fetch('/api/comments/comments', {
                method: 'POST',
                body: payload,
                headers: {
                    'X-CSRF-Token': csrfToken.value
                }
            })

            resetRecaptcha()
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
        renderRecaptcha()
    })

    return {
        submitting,
        error,
        submitComment
    }
}
