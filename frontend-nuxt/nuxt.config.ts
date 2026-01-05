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
      // Cloudflare Turnstile 金鑰
      turnstileSiteKey: process.env.NUXT_PUBLIC_TURNSTILE_SITE_KEY || ''
    }
  },

  security: {
    headers: {
      contentSecurityPolicy: {
        'default-src': ["'self'"],
        'script-src': [
          "'self'",
          "'unsafe-inline'", // Required for Nuxt hydration
          // 僅在開發模式允許 unsafe-eval
          ...(process.env.NODE_ENV === 'development' ? ["'unsafe-eval'"] : []),
          "https://challenges.cloudflare.com",
          "https://static.cloudflareinsights.com" // Cloudflare 分析
        ],
        'style-src': [
          "'self'",
          "'unsafe-inline'", // Required for Tailwind and dynamic styles
          "https://fonts.googleapis.com"
        ],
        'frame-src': [
          "'self'",
          "https://challenges.cloudflare.com",
          "https://web3.dgpa.gov.tw"
        ],
        'connect-src': [
          "'self'",
          // 開發模式允許本地 API
          ...(process.env.NODE_ENV === 'development' ? ["http://localhost:8002"] : []),
          "https://challenges.cloudflare.com"
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
        // Cloudflare Turnstile
        { src: 'https://challenges.cloudflare.com/turnstile/v0/api.js', async: true, defer: true }
      ]
    }
  },

  routeRules: {
    // Special case: Home page jobs fetch maps to backend root
    '/api/jobs': { proxy: 'http://localhost:8002/' },

    // General API proxy: /api/xxx -> http://localhost:8002/xxx
    '/api/**': { proxy: 'http://localhost:8002/**' },

    // LINE Bot webhook
    '/line_ai_bot/**': { proxy: 'http://localhost:8002/line_ai_bot/**' }
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
      navigateFallback: null, // 禁用 navigateFallback 避免 non-precached-url 錯誤
      globPatterns: ['**/*.{js,css,html,png,svg,ico}']
    },
    devOptions: {
      enabled: true,  // 開發模式也啟用 manifest 避免 404 警告
      type: 'module'
    }
  }
})
