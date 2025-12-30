// https://nuxt.com/docs/api/configuration/nuxt-config
// Force rebuild for tailwind config changes (Timestamp: 2024-12-25 15:30)
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  css: ['~/assets/main.css'],

  modules: [
    '@pinia/nuxt',
    '@vite-pwa/nuxt',
    '@nuxtjs/tailwindcss',
    'nuxt-security'
  ],

  runtimeConfig: {
    public: {
      // reCAPTCHA 金鑰必須透過環境變數設定，不使用硬編碼預設值
      recaptchaSiteKey: process.env.NUXT_PUBLIC_RECAPTCHA_SITE_KEY || ''
    }
  },

  security: {
    headers: {
      contentSecurityPolicy: {
        'default-src': ["'self'"],
        'script-src': [
          "'self'",
          "'unsafe-inline'", // Required for Nuxt hydration and reCAPTCHA callbacks
          // 僅在開發模式允許 unsafe-eval
          ...(process.env.NODE_ENV === 'development' ? ["'unsafe-eval'"] : []),
          "https://www.google.com",
          "https://www.gstatic.com"
        ],
        'style-src': [
          "'self'",
          "'unsafe-inline'", // Required for Tailwind and dynamic styles
          "https://fonts.googleapis.com"
        ],
        'frame-src': [
          "'self'",
          "https://www.google.com",
          "https://web3.dgpa.gov.tw"
        ],
        'connect-src': [
          "'self'",
          // 開發模式允許本地 API
          ...(process.env.NODE_ENV === 'development' ? ["http://localhost:8000"] : []),
          "https://www.google.com"
        ],
        'img-src': [
          "'self'",
          "data:",
          "https:",
          "blob:"
        ],
        'font-src': [
          "'self'",
          "https://fonts.gstatic.com"
        ],
        // 僅在生產環境啟用 HTTPS 升級
        'upgrade-insecure-requests': process.env.NODE_ENV === 'production'
      },
      crossOriginEmbedderPolicy: false, // 外部資源相容性
    }
  },

  app: {
    head: {
      link: [
        { rel: 'manifest', href: '/manifest.webmanifest' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap' }
      ],
      script: [
        { src: 'https://www.google.com/recaptcha/api.js?render=explicit', async: true, defer: true }
      ]
    }
  },

  routeRules: {
    // Special case: Home page jobs fetch maps to backend root
    '/api/jobs': { proxy: 'http://localhost:8000/' },

    // General API proxy: /api/xxx -> http://localhost:8000/xxx
    '/api/**': { proxy: 'http://localhost:8000/**' },

    // LINE Bot webhook
    '/line_ai_bot/**': { proxy: 'http://localhost:8000/line_ai_bot/**' }
  },

  pwa: {
    registerType: 'autoUpdate',
    manifest: {
      name: '開放事求人',
      short_name: '開放事求人',
      description: '公務人員職缺查詢系統',
      theme_color: '#337AB7',
      background_color: '#ffffff',
      display: 'standalone',
      icons: [
        {
          src: 'pwa-192x192.png',
          sizes: '192x192',
          type: 'image/png'
        },
        {
          src: 'pwa-512x512.png',
          sizes: '512x512',
          type: 'image/png'
        }
      ]
    },
    workbox: {
      navigateFallback: '/',
      globPatterns: ['**/*.{js,css,html,png,svg,ico}']
    },
    devOptions: {
      enabled: false,
      type: 'module'
    }
  }
})
