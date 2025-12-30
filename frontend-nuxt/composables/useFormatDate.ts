import { formatDistanceToNow, format } from 'date-fns'
import { zhTW } from 'date-fns/locale'

/**
 * Composable for date formatting utilities
 */
export const useFormatDate = () => {
    /**
     * Format date to relative time (e.g., "3 天前")
     */
    const formatRelative = (dateStr: string): string => {
        if (!dateStr) return ''
        try {
            const date = new Date(dateStr)
            return formatDistanceToNow(date, { addSuffix: true, locale: zhTW })
        } catch (e) {
            return dateStr
        }
    }

    /**
     * Format date to standard format (e.g., "2024/12/29 15:30")
     */
    const formatDateTime = (dateStr: string): string => {
        if (!dateStr) return ''
        try {
            const date = new Date(dateStr)
            return format(date, 'yyyy/MM/dd HH:mm', { locale: zhTW })
        } catch (e) {
            return dateStr
        }
    }

    /**
     * Format date only (e.g., "2024/12/29")
     */
    const formatDateOnly = (dateStr: string): string => {
        if (!dateStr) return ''
        try {
            const date = new Date(dateStr)
            return format(date, 'yyyy/MM/dd', { locale: zhTW })
        } catch (e) {
            return dateStr
        }
    }

    /**
     * Check if job is new (announced today or yesterday)
     * Supports both formats: "1141230" or "114/12/30"
     */
    const isNewJob = (announceDate: string | undefined): boolean => {
        if (!announceDate) return false
        try {
            let rocYear: number, month: number, day: number

            if (announceDate.includes('/')) {
                const parts = announceDate.split('/')
                if (parts.length !== 3) return false
                rocYear = parseInt(parts[0])
                month = parseInt(parts[1])
                day = parseInt(parts[2])
            } else {
                const str = announceDate.padStart(7, '0')
                rocYear = parseInt(str.slice(0, 3))
                month = parseInt(str.slice(3, 5))
                day = parseInt(str.slice(5, 7))
            }

            const westYear = rocYear + 1911
            const jobDate = new Date(westYear, month - 1, day)

            const today = new Date()
            today.setHours(0, 0, 0, 0)
            const yesterday = new Date(today)
            yesterday.setDate(yesterday.getDate() - 1)

            return jobDate >= yesterday
        } catch (e) {
            return false
        }
    }

    /**
     * Check if job is expired (date_to has passed)
     * Supports both formats: "1141230" or "114/12/30"
     */
    const isExpired = (dateTo: string | undefined): boolean => {
        if (!dateTo) return false
        try {
            let rocYear: number, month: number, day: number

            if (dateTo.includes('/')) {
                const parts = dateTo.split('/')
                if (parts.length !== 3) return false
                rocYear = parseInt(parts[0])
                month = parseInt(parts[1])
                day = parseInt(parts[2])
            } else {
                const str = dateTo.padStart(7, '0')
                rocYear = parseInt(str.slice(0, 3))
                month = parseInt(str.slice(3, 5))
                day = parseInt(str.slice(5, 7))
            }

            const westYear = rocYear + 1911
            const endDate = new Date(westYear, month - 1, day)
            endDate.setHours(23, 59, 59, 999) // End of day

            const now = new Date()

            return now > endDate
        } catch (e) {
            return false
        }
    }

    return {
        formatRelative,
        formatDateTime,
        formatDateOnly,
        isNewJob,
        isExpired
    }
}
