export { }

declare global {
    interface Window {
        grecaptcha: {
            render: (container: string, parameters: { sitekey: string }) => number
            reset: (widgetId: number) => void
            getResponse: (widgetId: number | null) => string
        }
    }
}
