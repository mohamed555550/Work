import { motion } from 'framer-motion'
import { Link, useNavigate } from 'react-router-dom'
import { useToggleChefFavorite, useToggleChefFollow } from '../hooks/useMarketplace'
import { findTrade, findTradeCategory } from '../data/trades'
import { useAuthStore } from '../stores/authStore'
import type { Seller } from '../types/marketplace'

interface ChefCardProps {
  chef: Seller
  index?: number
}

function Initials({ name }: { name: string }) {
  return (
    <span className="grid h-full w-full place-items-center bg-gradient-to-br from-emerald-100 to-sky-100 text-2xl font-black text-forest-800">
      {name.trim().slice(0, 1)}
    </span>
  )
}

export function formatArabicTime(value?: string) {
  if (!value) return '--'
  const [hoursRaw, minutesRaw = '00'] = value.slice(0, 5).split(':')
  const hours = Number(hoursRaw)
  if (!Number.isFinite(hours)) return value
  const period = hours >= 12 ? 'مساء' : 'صباحا'
  const hour12 = hours % 12 || 12
  return minutesRaw === '00' ? `${hour12} ${period}` : `${hour12}:${minutesRaw} ${period}`
}

export default function ChefCard({ chef, index = 0 }: ChefCardProps) {
  const navigate = useNavigate()
  const authenticated = useAuthStore((state) => Boolean(state.accessToken))
  const follow = useToggleChefFollow()
  const favorite = useToggleChefFavorite()
  const selectedTrade = chef.professions?.[0]
  const trade = selectedTrade ? findTrade(selectedTrade.trade) : null
  const tradeCategory = selectedTrade ? findTradeCategory(selectedTrade.trade, selectedTrade.category) : null
  const locationText = chef.pickupAddress || `${chef.governorate}، ${chef.center}`
  const workHours = `من ${formatArabicTime(chef.workStartTime)} إلى ${formatArabicTime(chef.workEndTime)}`

  const requireAuth = (action: () => void) => {
    if (!authenticated) {
      navigate('/auth')
      return
    }
    action()
  }

  return (
    <motion.article
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: Math.min(index * 0.025, 0.12), duration: 0.2 }}
      whileHover={{ y: -2 }}
      role="link"
      tabIndex={0}
      aria-label={`عرض ملف ${chef.name}`}
      onClick={() => navigate(`/chefs/${chef.id}`)}
      onKeyDown={(event) => {
        if ((event.key === 'Enter' || event.key === ' ') && event.target === event.currentTarget) {
          event.preventDefault()
          navigate(`/chefs/${chef.id}`)
        }
      }}
      className="group cursor-pointer overflow-hidden rounded-2xl border border-[#d8e3dd] bg-white shadow-card transition-shadow hover:shadow-float focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2"
    >
      <div className="relative h-44 overflow-hidden bg-gradient-to-br from-forest-900 via-emerald-900 to-sky-900">
        {chef.coverImage && (
          <img
            src={chef.coverImage}
            alt={`غلاف ${chef.name}`}
            loading="lazy"
            className="h-full w-full object-cover transition duration-700 group-hover:scale-105"
          />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-forest-950/80 via-forest-950/10 to-black/10" />
        <button
          type="button"
          aria-label={chef.isFavorite ? 'إزالة العامل من المفضلة' : 'إضافة العامل للمفضلة'}
          aria-pressed={chef.isFavorite}
          disabled={favorite.isPending}
          onClick={(event) => {
            event.stopPropagation()
            requireAuth(() => favorite.mutate({ id: chef.id, favorite: chef.isFavorite }))
          }}
          className={`absolute left-3 top-3 grid h-10 w-10 place-items-center rounded-full border backdrop-blur-md transition ${
            chef.isFavorite
              ? 'border-rose-200 bg-rose-50/95 text-rose-600'
              : 'border-white/60 bg-black/20 text-white hover:bg-white hover:text-rose-600'
          }`}
        >
          <span aria-hidden="true">{chef.isFavorite ? '♥' : '♡'}</span>
        </button>
        <div className="absolute bottom-3 left-3 right-3 flex flex-wrap items-center justify-between gap-2">
          <span className={`rounded-full border px-3 py-1 text-[11px] font-black backdrop-blur ${
            chef.isOpen
              ? 'border-emerald-200 bg-emerald-50/95 text-emerald-700'
              : 'border-stone-200 bg-stone-100/95 text-stone-600'
          }`}>
            {chef.isOpen ? 'متاح الآن' : 'غير متاح الآن'}
          </span>
          <span className="rounded-full border border-white/25 bg-black/62 px-3 py-1 text-[11px] font-black text-white backdrop-blur">
            مواعيد العمل: {workHours}
          </span>
        </div>
      </div>

      <div className="relative px-5 pb-5 pt-12">
        <div className="absolute -top-11 right-5 h-[5.5rem] w-[5.5rem] overflow-hidden rounded-2xl border-4 border-white bg-brand-50 shadow-lg">
          {chef.profileImage ? (
            <img src={chef.profileImage} alt={chef.name} loading="lazy" className="h-full w-full object-cover" />
          ) : (
            <Initials name={chef.name} />
          )}
        </div>

        <div className="min-w-0">
          <h2 className="truncate text-lg font-black">{chef.name}</h2>
          {trade && (
            <p className="mt-2 inline-flex max-w-full items-center gap-1 rounded-full bg-forest-50 px-2.5 py-1 text-[11px] font-black text-forest-800">
              <span aria-hidden="true">{trade.icon}</span>
              <span className="truncate">{selectedTrade.title || `${trade.name} - ${tradeCategory?.name || ''}`}</span>
            </p>
          )}
          <p className="mt-3 line-clamp-2 text-sm leading-6 text-stone-600">
            <span className="font-black text-stone-800">المكان: </span>
            {locationText}
          </p>

          <div className="mt-3 rounded-2xl border border-emerald-100 bg-gradient-to-l from-emerald-50 to-sky-50 px-3 py-2 shadow-sm">
            <p className="text-[11px] font-black text-emerald-700">مواعيد العمل</p>
            <p className="mt-1 text-sm font-black text-forest-950">{workHours}</p>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2">
          <Link onClick={(event) => event.stopPropagation()} to={`/chefs/${chef.id}`} className="rounded-xl bg-forest-800 px-4 py-3 text-center text-xs font-bold text-white transition hover:bg-forest-700">
            راسل العامل
          </Link>
          <button
            type="button"
            aria-pressed={chef.isFollowing}
            disabled={follow.isPending}
            onClick={(event) => {
              event.stopPropagation()
              requireAuth(() => follow.mutate({ id: chef.id, following: chef.isFollowing }))
            }}
            className={`rounded-xl border px-3 py-3 text-xs font-bold transition ${
              chef.isFollowing
                ? 'border-brand-200 bg-brand-50 text-brand-700'
                : 'border-brand-500 text-brand-600 hover:bg-brand-500 hover:text-white'
            }`}
          >
            {chef.isFollowing ? 'تتابعه' : 'متابعة'}
          </button>
        </div>
      </div>
    </motion.article>
  )
}
