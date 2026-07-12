import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || (
  import.meta.env.DEV ? 'http://127.0.0.1:8000/api/v1' : '/api/v1'
)

const api = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const request = error.config
    if (error.response?.status === 401 && !request?._retry && localStorage.getItem('refreshToken')) {
      request._retry = true
      try {
        const response = await axios.post(`${api.defaults.baseURL}/refresh`, {
          refresh: localStorage.getItem('refreshToken'),
        })
        const payload = response.data?.data ?? response.data
        const access = payload.access
        const refresh = payload.refresh
        useAuthStore.getState().updateTokens(access, refresh)
        request.headers.Authorization = `Bearer ${access}`
        return api(request)
      } catch {
        useAuthStore.getState().logout()
        window.dispatchEvent(new Event('auth:logout'))
      }
    }
    return Promise.reject(error.response?.data || { error: error.message })
  },
)

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default api
