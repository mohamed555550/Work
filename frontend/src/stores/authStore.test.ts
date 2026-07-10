import { beforeEach, describe, expect, it } from 'vitest'
import { useAuthStore } from './authStore'

const user = {
  id: 1,
  username: 'alaa',
  email: 'alaa@example.com',
  role: 'user' as const,
  first_name: 'آلاء',
  last_name: 'محمد',
  email_verified: true,
}

describe('auth store', () => {
  beforeEach(() => {
    localStorage.clear()
    useAuthStore.setState({ accessToken: null, refreshToken: null, profile: null })
  })

  it('persists and clears a complete session', () => {
    useAuthStore.getState().setSession({ access: 'access', refresh: 'refresh', user })
    expect(useAuthStore.getState().profile?.email).toBe(user.email)
    expect(localStorage.getItem('accessToken')).toBe('access')

    useAuthStore.getState().logout()
    expect(useAuthStore.getState().accessToken).toBeNull()
    expect(localStorage.getItem('user')).toBeNull()
  })

  it('updates rotated tokens', () => {
    useAuthStore.getState().setSession({ access: 'old', refresh: 'old-refresh', user })
    useAuthStore.getState().updateTokens('new', 'new-refresh')
    expect(useAuthStore.getState().accessToken).toBe('new')
    expect(localStorage.getItem('refreshToken')).toBe('new-refresh')
  })
})
