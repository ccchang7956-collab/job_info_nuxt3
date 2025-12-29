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
      recaptchaSiteKey: process.env.NUXT_PUBLIC_RECAPTCHA_SITE_KEY || '6LeEYrMqAAAAAOwsV1pF_EoPxSJjvE49tz2nIQbC'
    }
  },

  security: {
    headers: {
      contentSecurityPolicy: {
        'default-src': ["'self'"],
        'script-src': [
          "'self'",
          "'unsafe-inline'", // Required for some Nuxt functionality and reCAPTCHA callbacks
          "'unsafe-eval'", // Sometimes needed for dev mode
          "https://www.google.com",
          "https://www.gstatic.com"
        ],
        'style-src': [
          "'self'",
          "'unsafe-inline'",
          "https://fonts.googleapis.com"
        ],
        'frame-src': [
          "'self'",
          "https://www.google.com",
          "https://web3.dgpa.gov.tw"
        ],
        'connect-src': [
          "'self'",
          "http://localhost:8000",
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
        'upgrade-insecure-requests': false // Disable for localhost dev
      },
      crossOriginEmbedderPolicy: false, // Often causes issues with external resources
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
