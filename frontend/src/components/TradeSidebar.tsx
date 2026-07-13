import { useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { selectableTrades as trades } from '../data/trades'
import { useUiStore } from '../stores/uiStore'

export default function TradeSidebar() {
  const { trade, tradeCategory, setTrade, setSidebarOpen } = useUiStore()
  const [expanded, setExpanded] = useState(trade)
  const [search, setSearch] = useState('')

  const visibleTrades = useMemo(() => {
    const query = search.trim()
    if (!query) return trades
    return trades.filter((item) => item.name.includes(query) || item.categories.some((category) => category.name.includes(query)))
  }, [search])

  return (
    <div className="flex min-h-0 flex-col bg-white/50 backdrop-blur-xl">
      <div className="border-b border-white/55 bg-white/35 p-3 sm:p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="eyebrow">المهن والصناعات</p>
            <h2 className="mt-1 text-base font-extrabold text-forest-900 sm:text-lg">اختار الصنعة</h2>
          </div>
          <button type="button" onClick={() => setSidebarOpen(false)} className="grid h-8 w-8 place-items-center rounded-full bg-brand-50 text-xl text-forest-900 lg:hidden" aria-label="إغلاق">×</button>
        </div>
        <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="نجار، كهربائي، عمال مصانع..." className="field-control mt-3" />
      </div>

      <div className="min-h-0 flex-1 space-y-2 overflow-y-auto overscroll-contain p-2 sm:p-3">
        {visibleTrades.map((item) => {
          const open = expanded === item.id
          const selectedTrade = trade === item.id
          return (
            <div key={item.id} className={`overflow-hidden rounded-xl border transition ${selectedTrade ? 'border-brand-300 bg-white/95 shadow-md' : 'border-white/55 bg-white/70 shadow-sm hover:bg-white/90'}`}>
              <button type="button" onClick={() => { setExpanded(open ? '' : item.id); setTrade(item.id, '') }} aria-expanded={open} className="flex w-full items-center justify-between gap-2 px-2.5 py-3 text-right text-xs font-bold sm:text-sm">
                <span className="flex min-w-0 items-center gap-2">
                  <span className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-brand-50 text-base text-brand-700 ring-1 ring-brand-100" aria-hidden="true">{item.icon}</span>
                  <span className="truncate">{item.name}</span>
                </span>
                <motion.span animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.18 }} className="text-brand-600" aria-hidden="true">⌄</motion.span>
              </button>
              <AnimatePresence initial={false}>
                {open && (
                  <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.16 }} className="overflow-hidden bg-[#f8fbff]">
                    <div className="grid max-h-72 gap-1 overflow-y-auto border-t border-[#dfe7f3] p-2">
                      <button type="button" onClick={() => { setTrade(item.id, ''); setSidebarOpen(false) }} className={`rounded-xl px-2.5 py-2 text-right text-xs transition sm:text-sm ${trade === item.id && !tradeCategory ? 'bg-brand-600 font-bold text-white' : 'text-stone-600 hover:bg-white hover:text-brand-800'}`}>
                        كل تخصصات {item.name}
                      </button>
                      {item.categories.map((category) => {
                        const selected = trade === item.id && tradeCategory === category.id
                        return (
                          <button key={category.id} type="button" onClick={() => { setTrade(item.id, category.id); setSidebarOpen(false) }} className={`rounded-xl px-2.5 py-2 text-right text-xs transition sm:text-sm ${selected ? 'bg-forest-800 font-bold text-white' : 'text-stone-600 hover:bg-white hover:text-forest-900'}`}>
                            {category.name}
                          </button>
                        )
                      })}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )
        })}
      </div>
    </div>
  )
}
