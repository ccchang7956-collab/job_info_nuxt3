declare global {
    interface Window {
        grecaptcha: ReCaptchaV2.ReCaptcha;
    }
}

declare namespace ReCaptchaV2 {
    interface ReCaptcha {
        render(container: string | HTMLElement, parameters: Parameters): number;
        reset(widgetId?: number): void;
        getResponse(widgetId?: number): string;
    }

    interface Parameters {
        sitekey: string;
        theme?: 'light' | 'dark';
        size?: 'normal' | 'compact' | 'invisible';
        tabindex?: number;
        callback?: (response: string) => void;
        'expired-callback'?: () => void;
        'error-callback'?: () => void;
    }
}

export { };
