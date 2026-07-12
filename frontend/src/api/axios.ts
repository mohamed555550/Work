import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
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
        const response = await axios.post(`${api.defaults.baseURL}/users/refresh/`, {
          refresh: localStorage.getItem('refreshToken'),
        })
        const access = response.data.access
        const refresh = response.data.refresh
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
