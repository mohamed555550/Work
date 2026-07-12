import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

interface Props {
  children: ReactNode
  role?: 'seller' | 'admin'
}

export default function ProtectedRoute({ children, role }: Props) {
  const location = useLocation()
  const { accessToken, profile } = useAuthStore()
  if (!accessToken) return <Navigate to="/auth" replace state={{ from: location.pathname }} />

  const allowed = !role || (
    role === 'admin'
      ? Boolean(profile?.is_staff)
      : profile?.role === 'seller' || Boolean(profile?.is_staff)
  )
  return allowed ? children : <Navigate to="/profile" replace />
}
