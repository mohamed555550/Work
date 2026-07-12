import { Link, useLocation } from 'react-router-dom'
import { trades } from '../data/trades'
import { useUiStore } from '../stores/uiStore'

export default function FoodCategoryNav() {
  const location = useLocation()
  const { trade, setTrade } = useUiStore()
  const activeTrade = location.pathname === '/search'
    ? new URLSearchParams(location.search).get('trade') || trade
    : trade

  return (
    <nav aria-label="المهن والصناعات" className="w-full border-t border-[#dfe7e3] bg-white shadow-sm">
      <div className="mx-auto flex w-full max-w-7xl touch-pan-x gap-1.5 overflow-x-auto px-2 py-2 sm:px-6">
        {trades.map((item) => (
          <Link
            key={item.id}
            to={`/search?trade=${item.id}&category=${item.categories[0]?.id || ''}`}
            onClick={() => setTrade(item.id, item.categories[0]?.id)}
            className={`inline-flex shrink-0 items-center justify-center gap-1.5 rounded-xl px-3.5 py-2 text-xs font-bold whitespace-nowrap transition ${
              activeTrade === item.id
                ? 'bg-forest-800 text-white shadow-md shadow-forest-900/15'
                : 'text-stone-500 hover:bg-brand-50 hover:text-brand-700'
            }`}
          >
            <span aria-hidden="true">{item.icon}</span>
            {item.name}
          </Link>
        ))}
      </div>
    </nav>
  )
}
