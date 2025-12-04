// https://nuxt.com/docs/api/configuration/nuxt-config
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
        'script-src': [
          "'self'",
          "'unsafe-inline'", // Required for some Nuxt functionality and reCAPTCHA callbacks
          "https://www.google.com",
          "https://www.gstatic.com"
        ],
        'frame-src': [
          "'self'",
          "https://www.google.com"
        ],
        'img-src': [
          "'self'",
          "data:",
          "https:",
          "blob:"
        ],
        'upgrade-insecure-requests': true
      },
      crossOriginEmbedderPolicy: false, // Often causes issues with external resources
    }
  },

  app: {
    head: {
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
    manifest: {
      name: '開放事求人',
      short_name: '開放事求人',
      description: '公務人員職缺查詢系統',
      theme_color: '#2563eb',
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
      navigateFallback: '/'
    },
    devOptions: {
      enabled: true,
      type: 'module'
    }
  }
})
