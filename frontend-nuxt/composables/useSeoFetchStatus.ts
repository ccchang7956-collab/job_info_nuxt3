import type { Ref } from 'vue'

// A temporary API failure must not look like a successful, empty HTML page.
export const useSeoFetchStatus = (error: Ref<unknown>) => {
  if (!import.meta.server || !error.value) return
  const status = Number((error.value as { statusCode?: number }).statusCode)
  setResponseStatus(status >= 500 && status <= 599 ? status : 503)
  useResponseHeader('Cache-Control').value = 'no-store'
}
