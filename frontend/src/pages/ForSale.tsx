import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import ProductCard from '../components/ProductCard'
import { trades } from '../data/trades'
import { useProducts } from '../hooks/useMarketplace'
import { useUiStore } from '../stores/uiStore'

export default function ForSale() {
  const { governorate, center, setSidebarOpen } = useUiStore()
  const [selectedTrade, setSelectedTrade] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const activeTrade = trades.find((trade) => trade.id === selectedTrade)
  const params = useMemo(() => ({
    governorate,
    center,
    listing_type: 'sale',
    ...(selectedTrade && selectedTrade !== 'all' ? { trade: selectedTrade } : {}),
    ...(selectedCategory && selectedCategory !== 'all' ? { trade_category: selectedCategory } : {}),
  }), [center, governorate, selectedCategory, selectedTrade])
  const query = useProducts(params)
  const products = query.data?.products || []

  function chooseTrade(tradeId: string) {
    setSelectedTrade((current) => current === tradeId ? '' : tradeId)
    setSelectedCategory('')
  }

  return (
    <main className="page-shell">
      <section className="overflow-hidden rounded-3xl border border-white/45 bg-slate-950/45 shadow-[0_18px_55px_rgba(0,0,0,0.20)] backdrop-blur-xl">
        <div className="p-4 sm:p-5">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div className="max-w-3xl">
              <p className="eyebrow">للبيع</p>
              <h1 className="page-heading mt-1">حاجات الصنايعية المعروضة للبيع في {center}</h1>
              <p className="page-subtitle">
                قطع، أدوات، خامات، شغل جاهز، أو أي حاجة الصنايعية عايزين يبيعوها قريب منك.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button type="button" onClick={() => setSidebarOpen(true)} className="secondary-button">
                تغيير المركز
              </button>
              <Link to="/seller" className="primary-button">
                اعرض حاجة للبيع
              </Link>
            </div>
          </div>
        </div>

        <div className="border-t border-white/15 bg-white/92 p-3 sm:p-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-sm font-black text-slate-950">فلتر المعروضات</h2>
              <p className="text-xs font-semibold text-stone-500">اختار مهنة، أو سيبها على الكل.</p>
            </div>
            {(selectedTrade || selectedCategory) && (
              <button type="button" onClick={() => { setSelectedTrade(''); setSelectedCategory('') }} className="rounded-xl border border-brand-100 bg-brand-50 px-3 py-2 text-xs font-black text-brand-700 transition hover:bg-brand-100">
                إظهار الكل
              </button>
            )}
          </div>

          <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
            {trades.map((trade) => {
              const active = selectedTrade === trade.id
              return (
                <button
                  key={trade.id}
                  type="button"
                  onClick={() => chooseTrade(trade.id)}
                  className={`group flex min-h-14 items-center gap-2 rounded-2xl border px-3 py-2 text-right text-sm font-black transition duration-200 ${
                    active
                      ? 'border-brand-300 bg-brand-600 text-white shadow-lg shadow-brand-900/15'
                      : 'border-[#dfe7f3] bg-white text-stone-700 hover:-translate-y-0.5 hover:border-brand-200 hover:bg-brand-50 hover:text-brand-800 hover:shadow-md'
                  }`}
                >
                  <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-xl transition ${active ? 'bg-white/15 text-white' : 'bg-brand-50 text-brand-700 group-hover:bg-white'}`}>{trade.icon}</span>
                  <span className="min-w-0 truncate">{trade.name}</span>
                </button>
              )
            })}
          </div>

          {activeTrade && activeTrade.id !== 'all' && (
            <div className="mt-4 rounded-2xl border border-[#dfe7f3] bg-[#f8fbff] p-3">
              <div className="mb-2 flex items-center justify-between gap-2">
                <p className="text-xs font-black text-slate-900">تخصصات {activeTrade.name}</p>
                <button
                  type="button"
                  onClick={() => setSelectedCategory('')}
                  className={`rounded-full px-3 py-1.5 text-xs font-bold transition ${!selectedCategory ? 'bg-brand-600 text-white' : 'bg-white text-stone-600 hover:text-brand-700'}`}
                >
                  كل التخصصات
                </button>
              </div>
              <div className="flex gap-2 overflow-x-auto pb-1">
                {activeTrade.categories.map((category) => (
                  <button
                    key={category.id}
                    type="button"
                    onClick={() => setSelectedCategory(category.id)}
                    className={`shrink-0 rounded-full px-4 py-2 text-xs font-bold transition ${
                      selectedCategory === category.id
                        ? 'bg-forest-800 text-white shadow-md shadow-forest-900/15'
                        : 'bg-white text-stone-600 hover:bg-brand-50 hover:text-brand-700'
                    }`}
                  >
                    {category.name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>

      <section className="mt-7 grid grid-cols-2 gap-3 lg:grid-cols-3 xl:grid-cols-4">
        {query.isLoading && [1, 2, 3, 4].map((item) => <div key={item} className="h-80 animate-pulse rounded-3xl bg-white/80" />)}
        {!query.isLoading && products.length === 0 && (
          <p className="surface-card col-span-full p-10 text-center text-stone-500">
            مفيش حاجات معروضة للبيع في المركز ده حاليا.
          </p>
        )}
        {products.map((product) => <ProductCard key={product.id} product={product} compact />)}
      </section>
    </main>
  )
}
