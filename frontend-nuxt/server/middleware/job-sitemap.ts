import { defineEventHandler, getRequestURL, proxyRequest } from 'h3'

export default defineEventHandler((event) => {
  const { pathname } = getRequestURL(event)
  if (!/^\/sitemap-jobs-[1-9]\d*\.xml$/.test(pathname)) return

  const config = useRuntimeConfig(event)
  const backendUrl = String(config.backendUrl).replace(/\/$/, '')
  return proxyRequest(event, `${backendUrl}${pathname}`)
})
