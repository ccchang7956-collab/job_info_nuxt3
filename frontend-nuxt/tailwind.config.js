/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./components/**/*.{js,vue,ts}",
        "./layouts/**/*.vue",
        "./pages/**/*.vue",
        "./plugins/**/*.{js,ts}",
        "./app.vue",
        "./error.vue"
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['"Noto Sans TC"', 'system-ui', '-apple-system', 'sans-serif'],
            },
            colors: {
                primary: {
                    50: '#f4f8fb',
                    100: '#e3eff6',
                    200: '#cce0ef',
                    300: '#99c2e2',
                    400: '#66a3d3',
                    500: '#408cc4',
                    600: '#337AB7', // Base color requested by user
                    700: '#296292',
                    800: '#204d74',
                    900: '#1a3e5c',
                    950: '#11283d',
                },
            },
            animation: {
                'fade-in': 'fadeIn 0.3s ease-out',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0', transform: 'translateY(-4px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                }
            }
        },
    },
    plugins: [],
}
