export const useSiteUrl = () => {
  const config = useRuntimeConfig()
  const siteUrl = config.public.siteUrl || 'https://opendgpa.shibaalin.com'

  return String(siteUrl).replace(/\/$/, '')
}

export const useAbsoluteUrl = (path = '/') => {
  const siteUrl = useSiteUrl()
  const normalizedPath = path.startsWith('/') ? path : `/${path}`

  return `${siteUrl}${normalizedPath}`
}
