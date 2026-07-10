import { useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { trades } from '../data/trades'
import { useUiStore } from '../stores/uiStore'

export default function TradeSidebar() {
  const { trade, tradeCategory, setTrade, setSidebarOpen } = useUiStore()
  const [expanded, setExpanded] = useState(trade)
  const [search, setSearch] = useState('')

  const visibleTrades = useMemo(() => {
    const query = search.trim()
    if (!query) return trades
    return trades.filter((item) => (
      item.name.includes(query)
      || item.categories.some((category) => category.name.includes(query))
    ))
  }, [search])

  return (
    <div className="flex h-full flex-col bg-white/45 backdrop-blur-xl">
      <div className="border-b border-white/55 bg-white/35 p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="eyebrow">المهن والصناعات</p>
            <h2 className="mt-1 text-lg font-extrabold tracking-tight text-forest-900">اختار الصنعة</h2>
          </div>
          <button
            type="button"
            onClick={() => setSidebarOpen(false)}
            className="grid h-9 w-9 place-items-center rounded-full bg-brand-50 text-forest-900 transition hover:bg-brand-100 lg:hidden"
            aria-label="إغلاق قائمة المهن"
          >
            <span aria-hidden="true">×</span>
          </button>
        </div>
        <label className="mt-3 block">
          <span className="sr-only">البحث في المهن</span>
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="نجار، كهربائي، عمال مصانع..."
            className="field-control"
          />
        </label>
      </div>

      <div className="flex-1 space-y-2 overflow-y-auto overscroll-contain p-3">
        {visibleTrades.map((item) => {
          const open = expanded === item.id
          const selectedTrade = trade === item.id
          return (
            <div
              key={item.id}
              className={`overflow-hidden rounded-2xl border transition-colors duration-200 ${
                selectedTrade
                  ? 'border-brand-300 bg-white/95 shadow-[0_10px_26px_rgba(37,99,235,0.16)]'
                  : 'border-white/55 bg-white/70 shadow-sm hover:border-brand-100 hover:bg-white/90'
              }`}
            >
              <button
                type="button"
                onClick={() => {
                  setExpanded(open ? '' : item.id)
                  setTrade(item.id, '')
                }}
                aria-expanded={open}
                className="flex w-full items-center justify-between px-3 py-3 text-right text-sm font-bold transition hover:bg-brand-50/75"
              >
                <span className="flex min-w-0 items-center gap-2">
                  <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-brand-50 text-base text-brand-700 ring-1 ring-brand-100" aria-hidden="true">{item.icon}</span>
                  <span className="truncate">{item.name}</span>
                </span>
                <motion.span animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.18 }} className="text-brand-600" aria-hidden="true">
                  ⌄
                </motion.span>
              </button>
              <AnimatePresence initial={false}>
                {open && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.16, ease: 'easeOut' }}
                    className="overflow-hidden bg-[#f8fbff]"
                  >
                    <div className="grid gap-1 border-t border-[#dfe7f3] p-2">
                      <button
                        type="button"
                        onClick={() => {
                          setTrade(item.id, '')
                          setSidebarOpen(false)
                        }}
                        className={`rounded-xl px-3 py-2 text-right text-sm transition ${
                          trade === item.id && !tradeCategory
                            ? 'bg-brand-600 font-bold text-white shadow-sm'
                            : 'text-stone-600 hover:bg-white hover:text-brand-800'
                        }`}
                      >
                        كل تخصصات {item.name}
                      </button>
                      {item.categories.map((category) => {
                        const selected = trade === item.id && tradeCategory === category.id
                        return (
                          <button
                            type="button"
                            key={category.id}
                            onClick={() => {
                              setTrade(item.id, category.id)
                              setSidebarOpen(false)
                            }}
                            className={`rounded-xl px-3 py-2 text-right text-sm transition ${
                              selected
                                ? 'bg-forest-800 font-bold text-white shadow-sm'
                                : 'text-stone-600 hover:bg-white hover:text-forest-900'
                            }`}
                          >
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
