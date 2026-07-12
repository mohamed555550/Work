export function dataOf<T>(response: any): T {
  return (response?.data?.data ?? response?.data ?? response) as T
}

export function listOf<T>(response: any): T[] {
  const body = response?.data ?? response
  const value = body?.results?.data ?? body?.results ?? body?.data ?? body
  return Array.isArray(value) ? value : []
}

export function errorMessage(error: any, fallback = 'حدث خطأ غير متوقع'): string {
  const value = error?.error ?? error?.detail ?? error?.message
  if (typeof value === 'string') return value
  if (value && typeof value === 'object') {
    const first = Object.values(value).flat()[0]
    if (typeof first === 'string') return first
  }
  return fallback
}
