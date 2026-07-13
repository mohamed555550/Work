import api from './axios'

export const auth = {
  register: (payload: unknown) => api.post('/register', payload),
  registerChef: (payload: unknown) => api.post('/users/register-chef/', payload),
  login: (payload: unknown) => api.post('/login', payload),
  refresh: (payload: unknown) => api.post('/refresh', payload),
  logout: (refresh: string) => api.post('/logout', { refresh }),
  verifyEmail: (payload: unknown) => api.post('/users/verify-email/', payload),
  forgotPassword: (payload: unknown) => api.post('/users/forgot-password/', payload),
  resetPassword: (payload: unknown) => api.post('/users/reset-password/', payload),
  profile: () => api.get('/me'),
  updateProfile: (payload: FormData | unknown) => api.put('/profile', payload, payload instanceof FormData ? { headers: { 'Content-Type': 'multipart/form-data' } } : undefined),
  sendSuggestion: (payload: { subject: string; message: string }) => api.post('/users/suggestions/', payload),
  adminUsers: () => api.get('/users/admin/users/'),
  adminUpdateUser: (id: number, payload: unknown) => api.patch(`/users/admin/users/${id}/`, payload),
  adminDeleteUser: (id: number) => api.delete(`/users/admin/users/${id}/`),
}

export const sellers = {
  locations: () => api.get('/sellers/locations/'),
  list: (params = {}) => api.get('/sellers/', { params }),
  detail: (id: number) => api.get(`/sellers/${id}/`),
  apply: (payload: unknown) => api.post('/sellers/apply/', payload),
  profile: () => api.get('/sellers/profile/'),
  updateProfile: (payload: FormData | unknown) => api.patch('/sellers/profile/', payload, payload instanceof FormData ? { headers: { 'Content-Type': 'multipart/form-data' } } : undefined),
  pending: () => api.get('/sellers/admin/pending/'),
  approve: (id: number, approved: 'approved' | 'rejected') => api.patch(`/sellers/${id}/approve/`, { approved }),
  follow: (id: number) => api.post(`/sellers/${id}/follow/`),
  unfollow: (id: number) => api.delete(`/sellers/${id}/follow/`),
  favorite: (id: number) => api.post(`/sellers/${id}/favorite/`),
  unfavorite: (id: number) => api.delete(`/sellers/${id}/favorite/`),
}

export const products = {
  aiSearch: (params: { q: string; governorate?: string; center?: string }) => api.get('/products/ai-search/', { params }),
  recommendations: (params: { governorate?: string; center?: string }) => api.get('/products/recommendations/', { params }),
  list: (params = {}) => api.get('/products/', { params }),
  detail: (id: number) => api.get(`/products/${id}/`),
  sellerProducts: () => api.get('/products/seller/'),
  adminProducts: () => api.get('/products/admin/all/'),
  create: (payload: FormData | unknown) => api.post('/products/create/', payload, payload instanceof FormData ? { headers: { 'Content-Type': 'multipart/form-data' } } : undefined),
  update: (id: number, payload: FormData | unknown) => api.patch(`/products/${id}/manage/`, payload, payload instanceof FormData ? { headers: { 'Content-Type': 'multipart/form-data' } } : undefined),
  remove: (id: number) => api.delete(`/products/${id}/manage/`),
}

export const orders = {
  list: () => api.get('/orders/'),
  detail: (id: number) => api.get(`/orders/${id}/`),
  create: (payload: unknown) => api.post('/orders/create/', payload),
  updateStatus: (id: number, status: string) => api.patch(`/orders/${id}/status/`, { status }),
  cancel: (id: number) => api.patch(`/orders/${id}/cancel/`),
}

export const reviews = {
  create: (payload: unknown) => api.post('/reviews/create/', payload),
  productReviews: (productId: number) => api.get(`/reviews/product/${productId}/`),
}

export const favorites = {
  list: () => api.get('/favorites/'),
  add: (payload: unknown) => api.post('/favorites/add/', payload),
  remove: (id: number) => api.delete(`/favorites/${id}/remove/`),
}

export const cart = {
  list: () => api.get('/cart/'),
  add: (payload: unknown) => api.post('/cart/add/', payload),
  update: (id: number, payload: unknown) => api.put(`/cart/${id}/update/`, payload),
  remove: (id: number) => api.delete(`/cart/${id}/remove/`),
}

export const notifications = {
  list: () => api.get('/notifications/'),
  markRead: (id: number) => api.patch(`/notifications/${id}/read/`),
  pushPublicKey: () => api.get('/notifications/push/public-key/'),
  pushSubscribe: (payload: unknown) => api.post('/notifications/push/subscribe/', payload),
}

export const chat = {
  withChef: (chefId: number) => api.post(`/chat/with-chef/${chefId}/`),
  conversations: (search = '') => api.get('/chat/conversations/', { params: search ? { search } : {} }),
  list: (orderId: number) => api.get(`/chat/order/${orderId}/`),
  send: (payload: FormData | unknown) => api.post('/chat/send/', payload),
  markRead: (orderId: number) => api.post(`/chat/order/${orderId}/read/`),
  deleteMessage: (id: number, scope: 'me' | 'everyone') => api.delete(`/chat/messages/${id}/`, { params: { scope } }),
}

export const support = {
  mine: () => api.get('/chat/support/'),
  conversations: (search = '') => api.get('/chat/support/conversations/', { params: search ? { search } : {} }),
  detail: (id: number) => api.get(`/chat/support/conversations/${id}/`),
  send: (message: string, conversationId?: number) => api.post('/chat/support/messages/', {
    message,
    ...(conversationId ? { conversation_id: conversationId } : {}),
  }),
  updateStatus: (id: number, status: 'open' | 'closed') => api.patch(`/chat/support/conversations/${id}/`, { status }),
}

export const auditLogs = {
  list: () => api.get('/audit/'),
}

export default api
