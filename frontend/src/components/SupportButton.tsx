import { Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export default function SupportButton() {
  const accessToken = useAuthStore((state) => state.accessToken)
  if (!accessToken) return null

  return (
    <Link
      to="/support"
      className="fixed bottom-24 left-4 z-30 inline-flex items-center gap-2 rounded-full border border-[#e8e3da] bg-white/95 px-4 py-3 text-xs font-black text-[#1d2624] shadow-2xl backdrop-blur transition hover:-translate-y-0.5 hover:bg-[#f7f4ef] md:bottom-6 md:left-6"
      aria-label="التواصل مع دعم صنعتى"
    >
      <span className="grid h-6 w-6 place-items-center rounded-full bg-forest-800 text-sm text-white">؟</span>
      دعم صنعتى
    </Link>
  )
}

