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

    return {
        formatRelative,
        formatDateTime,
        formatDateOnly
    }
}
