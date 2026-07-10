import { create } from 'zustand'

interface UiState {
  language: 'ar' | 'en'
  governorate: string
  center: string
  trade: string
  tradeCategory: string
  sidebarOpen: boolean
  recentSearches: string[]
  setLocation: (governorate: string, center: string) => void
  setTrade: (trade: string, tradeCategory?: string) => void
  setSidebarOpen: (open: boolean) => void
  addRecentSearch: (value: string) => void
  toggleLanguage: () => void
}

function storedSearches(): string[] {
  try {
    const value = JSON.parse(localStorage.getItem('recentSearches') || '[]')
    return Array.isArray(value) ? value.filter((item) => typeof item === 'string').slice(0, 5) : []
  } catch {
    return []
  }
}

export const useUiStore = create<UiState>((set) => ({
  language: 'ar',
  governorate: 'المنيا',
  center: 'مركز المنيا',
  trade: 'carpenter',
  tradeCategory: 'doors-windows',
  sidebarOpen: false,
  recentSearches: storedSearches(),
  setLocation: (governorate, center) => set({ governorate, center }),
  setTrade: (trade, tradeCategory = '') => set({ trade, tradeCategory }),
  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
  toggleLanguage: () => set(() => {
    localStorage.setItem('language', 'ar')
    return { language: 'ar' }
  }),
  addRecentSearch: (rawValue) => set((state) => {
    const value = rawValue.trim()
    if (!value) return state
    const recentSearches = [value, ...state.recentSearches.filter((item) => item !== value)].slice(0, 5)
    localStorage.setItem('recentSearches', JSON.stringify(recentSearches))
    return { recentSearches }
  }),
}))
