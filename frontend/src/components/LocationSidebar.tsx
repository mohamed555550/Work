import { useEffect, useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { egyptGovernorates } from '../data/egyptLocations'
import { useLocations } from '../hooks/useMarketplace'
import { useUiStore } from '../stores/uiStore'
import { cleanText } from '../utils/text'

function fallbackLocations() {
  return egyptGovernorates.map((governorate, index) => ({
    id: index + 1,
    icon: governorate.icon,
    name: governorate.name,
    name_ar: governorate.name,
    name_en: governorate.nameEn,
    slug: governorate.nameEn.toLowerCase().replace(/\s+/g, '-'),
    centers: governorate.centers.map((center, centerIndex) => ({
      id: (index + 1) * 100 + centerIndex,
      name: center,
      name_ar: center,
      name_en: center,
      slug: `${governorate.nameEn}-${centerIndex}`.toLowerCase(),
    })),
  }))
}

export default function LocationSidebar() {
  const { governorate, center, setLocation, setSidebarOpen } = useUiStore()
  const locationsQuery = useLocations()
  const localLocations = useMemo(() => fallbackLocations(), [])
  const locations = locationsQuery.data?.length ? locationsQuery.data : localLocations
  const [expanded, setExpanded] = useState(governorate)
  const [governorateSearch, setGovernorateSearch] = useState('')
  const [centerSearch, setCenterSearch] = useState('')

  useEffect(() => {
    if (!centerSearch.trim()) return
    const query = centerSearch.trim().toLowerCase()
    const match = locations.find((item) => item.centers.some((entry) => (
      cleanText(entry.name_ar).includes(centerSearch.trim()) || entry.name_en.toLowerCase().includes(query)
    )))
    if (match) setExpanded(match.name)
  }, [centerSearch, locations])

  const visible = useMemo(() => {
    const governorateQuery = governorateSearch.trim().toLowerCase()
    const centerQuery = centerSearch.trim().toLowerCase()
    return locations
      .filter((item) => !governorateQuery || cleanText(item.name_ar).includes(governorateSearch.trim()) || item.name_en.toLowerCase().includes(governorateQuery))
      .map((item) => ({
        ...item,
        centers: centerQuery
          ? item.centers.filter((entry) => cleanText(entry.name_ar).includes(centerSearch.trim()) || entry.name_en.toLowerCase().includes(centerQuery))
          : item.centers,
      }))
      .filter((item) => !centerQuery || item.centers.length > 0)
  }, [centerSearch, governorateSearch, locations])

  return (
    <div className="flex min-h-0 flex-col bg-white/45 backdrop-blur-xl">
      <div className="border-b border-white/55 bg-white/35 p-3 sm:p-4">
        <div className="flex items-center justify-between lg:hidden">
          <p className="text-sm font-black">المحافظات</p>
          <button type="button" onClick={() => setSidebarOpen(false)} className="grid h-8 w-8 place-items-center rounded-full bg-brand-50 text-xl text-brand-700" aria-label="إغلاق">×</button>
        </div>
        <input value={governorateSearch} onChange={(event) => setGovernorateSearch(event.target.value)} placeholder="ابحث عن محافظة" className="field-control mt-3 lg:mt-0" />
        <input value={centerSearch} onChange={(event) => setCenterSearch(event.target.value)} placeholder="ابحث عن مركز أو مدينة" className="field-control mt-2" />
        <div className="mt-3">
          <p className="eyebrow">نطاق البحث</p>
          <h2 className="mt-1 text-base font-extrabold text-forest-900 sm:text-lg">محافظات مصر</h2>
        </div>
      </div>

      <div className="min-h-0 flex-1 space-y-2 overflow-y-auto overscroll-contain p-2 sm:p-3">
        {locationsQuery.isLoading && <div className="h-14 animate-pulse rounded-xl bg-brand-50" />}
        {visible.map((item) => {
          const open = expanded === item.name
          return (
            <div key={item.id} className={`overflow-hidden rounded-xl border transition ${open ? 'border-brand-200 bg-white/95 shadow-md' : 'border-white/55 bg-white/70 shadow-sm'}`}>
              <button type="button" onClick={() => setExpanded(open ? '' : item.name)} aria-expanded={open} className="flex w-full items-center justify-between gap-2 px-2.5 py-3 text-right text-xs font-bold sm:text-sm">
                <span className="flex min-w-0 items-center gap-2">
                  <span className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-[#eef3f1] text-base" aria-hidden="true">{item.icon}</span>
                  <span className="truncate">{cleanText(item.name_ar)}</span>
                </span>
                <motion.span animate={{ rotate: open ? 180 : 0 }} className="text-brand-600" aria-hidden="true">⌄</motion.span>
              </button>
              <AnimatePresence initial={false}>
                {open && (
                  <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.18 }} className="overflow-hidden bg-[#fbfcfb]">
                    <div className="grid max-h-72 gap-1 overflow-y-auto border-t border-[#e4ebe7] p-2">
                      {item.centers.map((itemCenter) => {
                        const selected = governorate === item.name && center === itemCenter.name
                        return (
                          <button key={itemCenter.id} type="button" onClick={() => { setLocation(item.name, itemCenter.name); setSidebarOpen(false) }} className={`rounded-lg px-2.5 py-2 text-right text-xs transition sm:text-sm ${selected ? 'bg-forest-800 font-bold text-white' : 'text-stone-600 hover:bg-white hover:text-forest-900'}`}>
                            {cleanText(itemCenter.name_ar)}
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
