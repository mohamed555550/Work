import { create } from 'zustand'
import type { Session, UserProfile } from '../types/marketplace'

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  profile: UserProfile | null
  setSession: (session: Session) => void
  updateTokens: (access: string, refresh?: string) => void
  setProfile: (profile: UserProfile) => void
  logout: () => void
}

function readProfile(): UserProfile | null {
  try {
    return JSON.parse(localStorage.getItem('user') || 'null')
  } catch {
    localStorage.removeItem('user')
    return null
  }
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: localStorage.getItem('accessToken'),
  refreshToken: localStorage.getItem('refreshToken'),
  profile: readProfile(),
  setSession: ({ access, refresh, user }) => {
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
    localStorage.setItem('user', JSON.stringify(user))
    set({ accessToken: access, refreshToken: refresh, profile: user })
  },
  updateTokens: (access, refresh) => {
    localStorage.setItem('accessToken', access)
    if (refresh) localStorage.setItem('refreshToken', refresh)
    set((state) => ({ accessToken: access, refreshToken: refresh || state.refreshToken }))
  },
  setProfile: (profile) => {
    localStorage.setItem('user', JSON.stringify(profile))
    set({ profile })
  },
  logout: () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
    set({ accessToken: null, refreshToken: null, profile: null })
  },
}))
