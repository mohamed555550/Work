import { lazy, Suspense, useEffect } from 'react'
import { HashRouter, Link, NavLink, Route, Routes, useLocation } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import BottomNav from './components/BottomNav'
import LocationSidebar from './components/LocationSidebar'
import TradeSidebar from './components/TradeSidebar'
import SuggestionButton from './components/SuggestionButton'
import SupportButton from './components/SupportButton'
import WorkerBackground from './components/EgyptianFoodBackground'
import ProtectedRoute from './components/ProtectedRoute'
import { auth } from './api'
import { queryClient } from './lib/queryClient'
import { usePushNotifications, useRealtimeNotifications } from './hooks/useRealtime'
import { useAuthStore } from './stores/authStore'
import { useUiStore } from './stores/uiStore'
import { publicAsset } from './utils/assets'
import type { UserProfile } from './types/marketplace'

const AdminDashboard = lazy(() => import('./pages/AdminDashboard'))
const Auth = lazy(() => import('./pages/Auth'))
const Chat = lazy(() => import('./pages/Chat'))
const ChefDetail = lazy(() => import('./pages/ChefDetail'))
const Chefs = lazy(() => import('./pages/Chefs'))
const Favorites = lazy(() => import('./pages/Favorites'))
const Home = lazy(() => import('./pages/Home'))
const Privacy = lazy(() => import('./pages/Legal').then((module) => ({ default: module.Privacy })))
const Terms = lazy(() => import('./pages/Legal').then((module) => ({ default: module.Terms })))
const NotFound = lazy(() => import('./pages/NotFound'))
const Notifications = lazy(() => import('./pages/Notifications'))
const ProductDetail = lazy(() => import('./pages/ProductDetail'))
const Profile = lazy(() => import('./pages/Profile'))
const Search = lazy(() => import('./pages/Search'))
const SellerDashboard = lazy(() => import('./pages/SellerDashboard'))
const SupportChat = lazy(() => import('./pages/SupportChat'))
const ForSale = lazy(() => import('./pages/ForSale'))

function ApplicationShell() {
  const location = useLocation()
  const isHome = location.pathname === '/'
  const { accessToken, setProfile, logout } = useAuthStore()
  const { governorate, center, sidebarOpen, setSidebarOpen } = useUiStore()
  useRealtimeNotifications()
  usePushNotifications()

  useEffect(() => {
    if (!accessToken) return
    auth.profile()
      .then((response) => setProfile(response.data.data as UserProfile))
      .catch(() => undefined)
  }, [accessToken, setProfile])

  useEffect(() => {
    const handleLogout = () => {
      logout()
      queryClient.clear()
    }
    window.addEventListener('auth:logout', handleLogout)
    return () => window.removeEventListener('auth:logout', handleLogout)
  }, [logout])

  useEffect(() => {
    if (!sidebarOpen) return
    const previousOverflow = document.body.style.overflow
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setSidebarOpen(false)
    }
    document.body.style.overflow = 'hidden'
    window.addEventListener('keydown', handleEscape)
    return () => {
      document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', handleEscape)
    }
  }, [setSidebarOpen, sidebarOpen])

  return (
    <div dir="rtl" className="relative isolate min-h-screen text-[#1d2624]">
      <WorkerBackground />
      <header className="sticky top-0 z-30 border-b border-white/35 bg-white/30 shadow-[0_12px_36px_rgba(18,15,11,0.28)] backdrop-blur-xl">
        <div className="mx-auto flex max-w-[1500px] items-center justify-between gap-3 px-4 py-3 sm:px-6">
          <div className="flex items-center gap-3">
            <button onClick={() => setSidebarOpen(true)} className="grid h-10 w-10 place-items-center rounded-xl border border-[#ece7df] bg-white text-forest-800 shadow-sm lg:hidden" aria-label="اختيار الموقع">☰</button>
            <Link to="/" className="grid h-11 w-11 shrink-0 place-items-center overflow-hidden rounded-full bg-[#e6f2bd]" aria-label="صنعتى">
              <img src={publicAsset('/brand/sanati-mark.png')} alt="" className="h-full w-full object-contain" />
            </Link>
            <div className="hidden sm:block">
              <Link to="/" className="text-lg font-extrabold text-[#242424]">صنعتى</Link>
              <button onClick={() => setSidebarOpen(true)} className="block max-w-52 truncate text-[11px] font-semibold text-stone-500 lg:cursor-default" type="button">
                <span className="text-brand-500">●</span> {governorate} · {center}
              </button>
            </div>
          </div>
          <nav className="hidden items-center gap-1 rounded-2xl bg-[#f6f4ef] p-1 text-xs font-bold md:flex">
            {[
              ['/', 'الرئيسية'],
              ['/chefs', 'الصنايعية'],
              ['/search', 'البحث'],
              ['/for-sale', 'للبيع'],
              ['/messages', 'الرسائل'],
            ].map(([to, label]) => (
              <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => `rounded-xl px-3.5 py-2 transition ${isActive ? 'bg-white text-forest-900 shadow-sm' : 'text-stone-500 hover:text-forest-800'}`}>
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            <Link to="/notifications" className="grid h-10 w-10 place-items-center rounded-xl border border-[#ece7df] bg-white text-lg transition hover:border-brand-200" aria-label="الإشعارات">🔔</Link>
            <Link to={accessToken ? '/profile' : '/auth'} className="grid h-10 w-10 place-items-center rounded-xl bg-brand-500 text-xs font-extrabold text-white shadow-lg shadow-brand-500/20">حساب</Link>
          </div>
        </div>
      </header>

      <div className="relative z-10 flex min-h-[calc(100vh-65px)]">
        {!isHome && (
          <aside className="hidden w-[36rem] shrink-0 grid-cols-2 border-l border-white/30 bg-white/20 shadow-[-14px_0_38px_rgba(18,15,11,0.24)] backdrop-blur-xl lg:sticky lg:top-[65px] lg:grid lg:h-[calc(100vh-65px)]">
            <LocationSidebar />
            <TradeSidebar />
          </aside>
        )}
        <AnimatePresence>
          {sidebarOpen && (
            <>
              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className={`fixed inset-0 z-40 bg-black/35 backdrop-blur-[1px] ${isHome ? '' : 'lg:hidden'}`}
                onClick={() => setSidebarOpen(false)}
                aria-label="إغلاق القائمة"
              />
              <motion.aside
                initial={{ x: '100%' }}
                animate={{ x: 0 }}
                exit={{ x: '100%' }}
                transition={{ type: 'spring', stiffness: 360, damping: 34 }}
                role="dialog"
                aria-modal="true"
                aria-label="اختيار المحافظة والمركز"
                className={`fixed inset-y-0 right-0 z-50 grid w-[40rem] max-w-[96vw] grid-cols-1 overflow-hidden border-l border-white/30 bg-white/20 shadow-[-18px_0_50px_rgba(0,0,0,0.35)] backdrop-blur-2xl sm:grid-cols-2 ${isHome ? '' : 'lg:hidden'}`}
              >
                <LocationSidebar />
                <TradeSidebar />
              </motion.aside>
            </>
          )}
        </AnimatePresence>

        <div className="min-w-0 flex-1">
          <Suspense fallback={<div className="p-8 text-center">جاري تحميل الصفحة...</div>}><Routes>
            <Route path="/" element={<Home />} />
            <Route path="/search" element={<Search />} />
            <Route path="/for-sale" element={<ForSale />} />
            <Route path="/chefs" element={<Chefs />} />
            <Route path="/chefs/:id" element={<ChefDetail />} />
            <Route path="/products/:id" element={<ProductDetail />} />
            <Route path="/auth/*" element={<Auth />} />
            <Route path="/favorites" element={<ProtectedRoute><Favorites /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            <Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
            <Route path="/privacy" element={<Privacy />} />
            <Route path="/terms" element={<Terms />} />
            <Route path="/chat/:orderId" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
            <Route path="/messages" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
            <Route path="/support" element={<ProtectedRoute><SupportChat /></ProtectedRoute>} />
            <Route path="/seller" element={<ProtectedRoute role="seller"><SellerDashboard /></ProtectedRoute>} />
            <Route path="/admin" element={<ProtectedRoute role="admin"><AdminDashboard /></ProtectedRoute>} />
            <Route path="*" element={<NotFound />} />
          </Routes></Suspense>
          <footer className="border-t border-white/30 bg-stone-950/85 px-5 py-6 pb-24 text-center text-xs text-white/70 backdrop-blur md:pb-6">
            <p>© 2026 صنعتى - منصة عمال وخدمات قريبة منك</p>
            <div className="mt-2 flex justify-center gap-5">
              <Link to="/terms" className="hover:text-white">شروط الاستخدام</Link>
              <Link to="/privacy" className="hover:text-white">سياسة الخصوصية</Link>
            </div>
          </footer>
          <SuggestionButton />
          <SupportButton />
          <BottomNav />
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return <HashRouter><ApplicationShell /></HashRouter>
}
