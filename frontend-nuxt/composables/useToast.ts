import type { Toast } from '@/types'

export function useToast() {
    const toasts = useState<Toast[]>('toasts', () => [])

    const addToast = (message: string, type: 'success' | 'error' | 'info' = 'info', duration = 3000) => {
        const id = Date.now()
        toasts.value.push({ id, message, type })

        if (duration > 0) {
            setTimeout(() => {
                removeToast(id)
            }, duration)
        }
    }

    const removeToast = (id: number) => {
        const index = toasts.value.findIndex(t => t.id === id)
        if (index !== -1) {
            toasts.value.splice(index, 1)
        }
    }

    return {
        toasts,
        addToast,
        removeToast
    }
}
