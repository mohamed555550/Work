const baseUrl = import.meta.env.BASE_URL || '/'

function cleanBase() {
  return baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`
}

export function publicAsset(path: string) {
  if (!path) return ''
  if (/^(https?:|data:|blob:)/i.test(path)) return path
  const cleanPath = path.replace(/^\/+/, '')
  return `${cleanBase()}${cleanPath}`
}

export function apiOrigin() {
  const configured = import.meta.env.VITE_API_BASE_URL || ''
  if (/^https?:\/\//i.test(configured)) {
    return new URL(configured).origin
  }
  return ''
}

export function mediaUrl(path?: string | null, fallback = publicAsset('/backgrounds/trades/01-carpenter.jpg')) {
  if (!path) return fallback
  if (/^(https?:|data:|blob:)/i.test(path)) return path
  if (path.startsWith('/media/') || path.startsWith('/static/')) {
    const origin = apiOrigin()
    return origin ? `${origin}${path}` : path
  }
  return publicAsset(path)
}

export function imageFallback(event: SyntheticEvent<HTMLImageElement>, fallback = publicAsset('/backgrounds/trades/01-carpenter.jpg')) {
  const image = event.currentTarget
  if (image.dataset.fallbackApplied === 'true') return
  image.dataset.fallbackApplied = 'true'
  image.src = fallback
}
import type { SyntheticEvent } from 'react'
