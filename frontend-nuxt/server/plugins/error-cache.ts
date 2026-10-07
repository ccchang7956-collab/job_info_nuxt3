import { getResponseStatus, removeResponseHeader, setResponseHeader } from 'h3'

export default defineNitroPlugin((nitroApp) => {
  nitroApp.hooks.hook('beforeResponse', (event) => {
    // Nitro's SWR handler overwrites page-level Cache-Control even for errors.
    // It rejects error cache entries internally; prevent CDN caching as well.
    if (getResponseStatus(event) < 400) return
    setResponseHeader(event, 'Cache-Control', 'no-store')
    removeResponseHeader(event, 'ETag')
    removeResponseHeader(event, 'Last-Modified')
  })
})
