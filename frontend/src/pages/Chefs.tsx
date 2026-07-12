import ChefCard from '../components/ChefCard'
import { findTrade, findTradeCategory } from '../data/trades'
import { useChefs } from '../hooks/useMarketplace'
import { useUiStore } from '../stores/uiStore'

export default function Chefs() {
  const { governorate, center, trade, tradeCategory, setSidebarOpen } = useUiStore()
  const selectedTrade = findTrade(trade)
  const selectedCategory = tradeCategory ? findTradeCategory(trade, tradeCategory) : null
  const query = useChefs({
    governorate,
    center,
    trade,
    ...(tradeCategory ? { trade_category: tradeCategory } : {}),
  })
  const artisans = (query.data || []).flatMap((artisan) => {
    const matches = artisan.professions?.filter((item) => (
      item.trade === trade && (!tradeCategory || item.category === tradeCategory)
    ))
    if (!matches?.length) return [artisan]
    return matches.map((profession) => ({ ...artisan, professions: [profession] }))
  })

  return (
    <main className="page-shell">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="eyebrow">صنايعية قريبين منك</p>
          <h1 className="page-heading mt-1">{selectedCategory ? `${selectedTrade.name} - ${selectedCategory.name}` : `كل ${selectedTrade.name}`}</h1>
          <p className="page-subtitle">نتائج في {governorate} · {center}</p>
        </div>
        <button type="button" onClick={() => setSidebarOpen(true)} className="secondary-button lg:hidden">
          تغيير المهنة أو المركز
        </button>
      </div>
      <section className="mt-7 grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
        {query.isLoading && <p className="surface-card p-6 text-center">جاري تحميل الصنايعية...</p>}
        {!query.isLoading && artisans.length === 0 && (
          <p className="surface-card p-10 text-center text-stone-500">
            لا يوجد صنايعية متاحون في هذا المركز حاليا.
          </p>
        )}
        {artisans.map((artisan, index) => (
          <ChefCard key={`${artisan.id}-${artisan.professions?.[0]?.trade || 'profile'}-${artisan.professions?.[0]?.category || index}`} chef={artisan} index={index} />
        ))}
      </section>
    </main>
  )
}
