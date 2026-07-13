import { create } from 'zustand'
import type { Session, UserProfile, UserRole } from '../types/marketplace'

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  profile: UserProfile | null
  accountRole: UserRole | null
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
  accountRole: (localStorage.getItem('accountRole') as UserRole | null) || readProfile()?.role || null,
  setSession: ({ access, refresh, user }) => {
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
    localStorage.setItem('user', JSON.stringify(user))
    localStorage.setItem('accountRole', user.role)
    set({ accessToken: access, refreshToken: refresh, profile: user, accountRole: user.role })
  },
  updateTokens: (access, refresh) => {
    localStorage.setItem('accessToken', access)
    if (refresh) localStorage.setItem('refreshToken', refresh)
    set((state) => ({ accessToken: access, refreshToken: refresh || state.refreshToken }))
  },
  setProfile: (profile) => {
    localStorage.setItem('user', JSON.stringify(profile))
    localStorage.setItem('accountRole', profile.role)
    set({ profile, accountRole: profile.role })
  },
  logout: () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
    localStorage.removeItem('accountRole')
    set({ accessToken: null, refreshToken: null, profile: null, accountRole: null })
  },
}))
