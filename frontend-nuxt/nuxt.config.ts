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
    'nuxt-security',
    'nuxt-gtag'
  ],

  gtag: {
    id: process.env.NUXT_PUBLIC_GTAG_ID || 'G-216TMW7GFM'
  },

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
          "https://static.cloudflareinsights.com", // Cloudflare 分析
          "https://www.googletagmanager.com" // Google Analytics
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
          "https://challenges.cloudflare.com",
          "https://www.google-analytics.com",
          "https://analytics.google.com",
          "https://stats.g.doubleclick.net"
        ],
        'img-src': [
          "'self'",
          "data:",
          "https:",
          "blob:",
          "https://www.google-analytics.com",
          "https://*.google-analytics.com",
          "https://*.analytics.google.com",
          "https://*.googletagmanager.com"
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
      meta: [
        { name: 'google-site-verification', content: 'NqVWpaQNA2zQaG0iXjwamdwnSy0BX-GZ4Og4sWFKTGY' },
        { name: 'robots', content: 'index,follow' },
        { name: 'language', content: 'zh-TW' },
        { property: 'og:type', content: 'website' },
        { property: 'og:site_name', content: '開放事求人' },
        { property: 'og:image', content: 'https://opendgpa.shibaalin.com/og-image.png' },
        { property: 'og:image:width', content: '1200' },
        { property: 'og:image:height', content: '630' },
        { property: 'og:locale', content: 'zh_TW' },
        { name: 'twitter:card', content: 'summary_large_image' },
        { name: 'twitter:image', content: 'https://opendgpa.shibaalin.com/og-image.png' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' },
        { rel: 'manifest', href: '/manifest.webmanifest' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        // 預連接 API 伺服器 - 加速資料載入
        { rel: 'preconnect', href: 'https://opendgpa.shibaalin.com' },
        { rel: 'dns-prefetch', href: 'https://opendgpa.shibaalin.com' },
        // 預連接 Cloudflare - 加速 Turnstile 載入
        { rel: 'preconnect', href: 'https://challenges.cloudflare.com' },
        { rel: 'dns-prefetch', href: 'https://challenges.cloudflare.com' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap' }
      ],
      script: [
        // Cloudflare Turnstile
        { src: 'https://challenges.cloudflare.com/turnstile/v0/api.js', async: true, defer: true }
      ],
      htmlAttrs: {
        lang: 'zh-TW'
      }
    }
  },

  routeRules: {
    // Special case: Home page jobs fetch maps to backend root
    '/api/jobs': { proxy: 'http://localhost:8002/' },

    // General API proxy: /api/xxx -> http://localhost:8002/xxx
    '/api/**': { proxy: 'http://localhost:8002/**' },

    // Sitemap proxy
    '/sitemap.xml': { proxy: 'http://localhost:8002/sitemap.xml' },

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
      navigateFallback: '/',
      globPatterns: ['**/*.{js,css,html,png,svg,ico}']
    },
    devOptions: {
      enabled: true,  // 開發模式也啟用 manifest 避免 404 警告
      type: 'module'
    }
  }
})
