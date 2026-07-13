import { Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export default function SuggestionButton() {
  const profile = useAuthStore((state) => state.profile)

  if (!profile || !['user', 'seller'].includes(profile.role)) return null

  return (
    <Link
      to="/support"
      className="fixed bottom-40 right-4 z-30 inline-flex items-center gap-2 rounded-full bg-brand-500 px-4 py-3 text-xs font-black text-white shadow-float transition hover:-translate-y-0.5 hover:bg-brand-600 md:bottom-6 md:right-6"
      aria-label="فتح شات مباشر مع صاحب الموقع"
    >
      <span aria-hidden="true" className="grid h-6 w-6 place-items-center rounded-full bg-white/20 text-sm">↗</span>
      شات مع صاحب الموقع
    </Link>
  )
}
