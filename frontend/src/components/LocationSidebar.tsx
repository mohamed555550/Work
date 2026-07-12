import { useEffect, useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { egyptGovernorates } from '../data/egyptLocations'
import { useLocations } from '../hooks/useMarketplace'
import { useUiStore } from '../stores/uiStore'

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
  const hasRemoteLocations = Array.isArray(locationsQuery.data) && locationsQuery.data.length > 0
  const locations = hasRemoteLocations ? (locationsQuery.data || localLocations) : localLocations
  const [expanded, setExpanded] = useState(governorate)
  const [governorateSearch, setGovernorateSearch] = useState('')
  const [centerSearch, setCenterSearch] = useState('')

  useEffect(() => {
    if (!centerSearch.trim()) return
    const query = centerSearch.trim().toLowerCase()
    const match = locations.find((item) => (
      item.centers.some((entry) => (
        entry.name_ar.includes(centerSearch.trim())
        || entry.name_en.toLowerCase().includes(query)
      ))
    ))
    if (match) setExpanded(match.name)
  }, [centerSearch, locations])

  const visible = useMemo(() => {
    const governorateQuery = governorateSearch.trim().toLowerCase()
    const centerQuery = centerSearch.trim().toLowerCase()
    return locations
      .filter((item) => (
        !governorateQuery
        || item.name_ar.includes(governorateSearch.trim())
        || item.name_en.toLowerCase().includes(governorateQuery)
      ))
      .map((item) => ({
        ...item,
        centers: centerQuery
          ? item.centers.filter((entry) => (
            entry.name_ar.includes(centerSearch.trim())
            || entry.name_en.toLowerCase().includes(centerQuery)
          ))
          : item.centers,
      }))
      .filter((item) => !centerQuery || item.centers.length > 0)
  }, [centerSearch, governorateSearch, locations])

  return (
    <div className="flex h-full flex-col bg-white/35 backdrop-blur-xl">
      <div className="border-b border-white/45 bg-white/25 p-4">
        <div className="flex items-center justify-between lg:hidden">
          <p className="text-sm font-black">اختيار الموقع</p>
          <button
            type="button"
            onClick={() => setSidebarOpen(false)}
            className="grid h-9 w-9 place-items-center rounded-full bg-brand-50 text-xl text-brand-700 lg:hidden"
            aria-label="إغلاق قائمة المواقع"
          >
            ×
          </button>
        </div>
        <label className="mt-3 block lg:mt-0">
          <span className="sr-only">البحث في المحافظات</span>
          <input
            value={governorateSearch}
            onChange={(event) => setGovernorateSearch(event.target.value)}
            placeholder="ابحث عن محافظة"
            className="field-control"
          />
        </label>
        <label className="mt-2 block">
          <span className="sr-only">البحث في المراكز</span>
          <input
            value={centerSearch}
            onChange={(event) => setCenterSearch(event.target.value)}
            placeholder="ابحث عن مركز أو مدينة"
            className="field-control"
          />
        </label>
        <div className="mt-4">
          <p className="eyebrow">اختار نطاق البحث</p>
          <h2 className="mt-1 text-lg font-extrabold tracking-tight text-forest-900">محافظات مصر</h2>
        </div>
      </div>

      <div className="flex-1 space-y-2 overflow-y-auto overscroll-contain p-3">
        {locationsQuery.isLoading && !hasRemoteLocations && (
          <div className="space-y-2" aria-label="جاري تحميل المواقع">
            {[1, 2, 3, 4, 5].map((item) => <div key={item} className="h-14 animate-pulse rounded-xl bg-brand-50" />)}
          </div>
        )}
        {visible.length === 0 && (
          <p className="rounded-xl bg-stone-50 p-5 text-center text-sm text-stone-500">لا توجد نتائج مطابقة.</p>
        )}
        {visible.map((item) => {
          const open = expanded === item.name
          return (
            <div key={item.id} className={`overflow-hidden rounded-2xl border backdrop-blur-md transition ${open ? 'border-white/70 bg-white/90 shadow-[0_8px_24px_rgba(0,0,0,0.14)]' : 'border-white/45 bg-white/65 shadow-sm'}`}>
              <button
                type="button"
                onClick={() => setExpanded(open ? '' : item.name)}
                aria-expanded={open}
                className="flex w-full items-center justify-between px-3 py-3 text-right text-sm font-bold transition hover:bg-brand-50/70"
              >
                <span className="flex items-center gap-2">
                  <span className="grid h-8 w-8 place-items-center rounded-xl bg-[#eef3f1] text-base" aria-hidden="true">{item.icon}</span>
                  {item.name_ar}
                </span>
                <motion.span animate={{ rotate: open ? 180 : 0 }} className="text-brand-600" aria-hidden="true">⌄</motion.span>
              </button>
              <AnimatePresence initial={false}>
                {open && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.22, ease: 'easeOut' }}
                    className="overflow-hidden bg-[#fbfcfb]"
                  >
                    <div className="grid gap-1 border-t border-[#e4ebe7] p-2">
                      {item.centers.map((itemCenter) => {
                        const selected = governorate === item.name && center === itemCenter.name
                        return (
                          <button
                            type="button"
                            key={itemCenter.id}
                            onClick={() => {
                              setLocation(item.name, itemCenter.name)
                              setSidebarOpen(false)
                            }}
                            className={`rounded-lg px-3 py-2 text-right text-sm transition ${
                              selected
                                ? 'bg-forest-800 font-bold text-white shadow-sm'
                                : 'text-stone-600 hover:bg-white hover:text-forest-900'
                            }`}
                          >
                            {itemCenter.name_ar}
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
