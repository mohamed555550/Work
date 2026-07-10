import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'

const items = [
  { ar: 'الرئيسية', to: '/', icon: '⌂' },
  { ar: 'بحث', to: '/search', icon: '⌕' },
  { ar: 'للبيع', to: '/for-sale', icon: '▣' },
  { ar: 'الرسائل', to: '/messages', icon: '✉' },
  { ar: 'حسابي', to: '/profile', icon: '●' },
]

export default function BottomNav() {
  return (
    <nav className="fixed inset-x-3 bottom-3 z-30 rounded-2xl border border-white/80 bg-white/90 shadow-float backdrop-blur-xl md:hidden">
      <div className="mx-auto flex max-w-screen-sm items-center justify-around px-2 py-1.5">
        {items.map((item) => (
          <NavLink key={item.to} to={item.to} className="w-14 text-xs font-medium text-stone-500" end>
            {({ isActive }) => (
              <motion.div animate={{ y: isActive ? -2 : 0 }} className="flex flex-col items-center gap-1">
                <span className={`flex h-8 w-8 items-center justify-center rounded-xl text-base transition ${isActive ? 'bg-forest-800 text-white shadow-lg shadow-forest-900/15' : 'text-stone-400'}`}>
                  {item.icon}
                </span>
                <span className={isActive ? 'text-brand-700' : ''}>{item.ar}</span>
              </motion.div>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
