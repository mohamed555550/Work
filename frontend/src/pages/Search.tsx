import { FormEvent, useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import ChefCard from '../components/ChefCard'
import ProductCard from '../components/ProductCard'
import { findTrade, findTradeCategory } from '../data/trades'
import { useChefs, useProducts } from '../hooks/useMarketplace'
import { useUiStore } from '../stores/uiStore'

export default function Search() {
  const [searchParams] = useSearchParams()
  const {
    recentSearches,
    addRecentSearch,
    governorate,
    center,
    trade,
    tradeCategory,
    setTrade,
    setSidebarOpen,
  } = useUiStore()
  const [query, setQuery] = useState('')
  const [submittedQuery, setSubmittedQuery] = useState('')

  useEffect(() => {
    const requestedTrade = searchParams.get('trade')
    const requestedCategory = searchParams.get('category')
    if (requestedTrade) setTrade(requestedTrade, requestedCategory || '')
    setSubmittedQuery('')
  }, [searchParams, setTrade])

  const selectedTrade = findTrade(trade)
  const selectedCategory = tradeCategory ? findTradeCategory(trade, tradeCategory) : null
  const filterParams = {
    governorate,
    center,
    trade,
    ...(tradeCategory ? { trade_category: tradeCategory } : {}),
    ...(submittedQuery ? { search: submittedQuery } : {}),
  }
  const artisansQuery = useChefs(filterParams)
  const productsQuery = useProducts({ ...filterParams, listing_type: 'sale' })

  const artisans = useMemo(() => (artisansQuery.data || []).flatMap((artisan) => {
    const matches = artisan.professions?.filter((item) => (
      item.trade === trade && (!tradeCategory || item.category === tradeCategory)
    ))
    if (!matches?.length) return [artisan]
    return matches.map((profession) => ({ ...artisan, professions: [profession] }))
  }), [artisansQuery.data, trade, tradeCategory])
  const products = productsQuery.data?.products || []

  function runSearch(value: string) {
    const clean = value.trim()
    setSubmittedQuery(clean)
    if (clean) addRecentSearch(clean)
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    runSearch(query)
  }

  const loading = artisansQuery.isLoading || productsQuery.isLoading

  return (
    <main className="page-shell">
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="eyebrow">بحث الصنايعية</p>
            <h1 className="page-heading mt-1">{selectedCategory ? `${selectedTrade.name} - ${selectedCategory.name}` : `كل ${selectedTrade.name}`}</h1>
            <p className="page-subtitle">الموقع الحالي: {governorate}، {center}</p>
          </div>
          <button type="button" onClick={() => setSidebarOpen(true)} className="secondary-button">
            تغيير المهنة أو المركز
          </button>
        </div>

        <form onSubmit={submit} className="surface-card mt-6 p-4 sm:p-5">
          <div className="flex gap-2">
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={`ابحث داخل ${selectedTrade.name}: اسم عامل، خدمة، منتج...`}
              className="field-control min-w-0 flex-1 py-3.5"
            />
            <button type="submit" className="primary-button">بحث</button>
          </div>
          <div className="mt-4 flex gap-2 overflow-x-auto pb-1">
            <button
              type="button"
              onClick={() => setTrade(selectedTrade.id, '')}
              className={`shrink-0 rounded-xl px-4 py-2 text-xs font-bold transition ${!tradeCategory ? 'bg-brand-600 text-white shadow-md shadow-brand-900/15' : 'bg-[#eef3fb] text-stone-600 hover:bg-white hover:text-brand-700'}`}
            >
              كل التخصصات
            </button>
            {selectedTrade.categories.map((category) => (
              <button
                key={category.id}
                type="button"
                onClick={() => setTrade(selectedTrade.id, category.id)}
                className={`shrink-0 rounded-xl px-4 py-2 text-xs font-bold transition ${tradeCategory === category.id ? 'bg-forest-800 text-white shadow-md shadow-forest-900/15' : 'bg-[#eef3fb] text-stone-600 hover:bg-white hover:text-brand-700'}`}
              >
                {category.name}
              </button>
            ))}
          </div>
        </form>

        {recentSearches.length > 0 && (
          <section className="mt-5">
            <p className="mb-2 text-sm font-bold text-white/85 drop-shadow-md">عمليات بحث حديثة</p>
            <div className="flex flex-wrap gap-2">
              {recentSearches.map((item) => (
                <button key={item} onClick={() => runSearch(item)} className="rounded-full border border-brand-100 bg-white px-4 py-2 text-sm text-stone-600 transition hover:border-brand-300 hover:text-brand-700">
                  {item}
                </button>
              ))}
              {submittedQuery && <button onClick={() => { setSubmittedQuery(''); setQuery('') }} className="rounded-full px-4 py-2 text-sm font-bold text-brand-100 hover:text-white">مسح البحث</button>}
            </div>
          </section>
        )}

        {loading && (
          <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {[1, 2, 3].map((item) => <div key={item} className="h-80 animate-pulse rounded-3xl bg-white" />)}
          </div>
        )}

        {!loading && artisans.length > 0 && (
          <section className="mt-8">
            <div className="mb-4 inline-block rounded-2xl border border-white/20 bg-slate-950/55 px-4 py-3 text-white shadow-lg backdrop-blur-md">
              <h2 className="text-xl font-black">الصنايعية المطابقين</h2>
              <p className="text-sm text-white/75">كل كارت مرتبط بمهنة وفرع واضح، والتواصل يتم بالشات للاتفاق على المعاد والتفاصيل.</p>
            </div>
            <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
              {artisans.map((artisan, index) => (
                <ChefCard key={`${artisan.id}-${artisan.professions?.[0]?.trade || 'profile'}-${artisan.professions?.[0]?.category || index}`} chef={artisan} index={index} />
              ))}
            </div>
          </section>
        )}

        {!loading && products.length > 0 && (
          <section className="mt-8">
            <div className="mb-4 inline-block rounded-2xl border border-white/20 bg-slate-950/55 px-4 py-3 text-white shadow-lg backdrop-blur-md">
              <h2 className="text-xl font-black">منتجات للبيع في نفس المركز</h2>
              <p className="text-sm text-white/75">منتجات يعرضها الصنايعية، والتفاصيل والتسليم يتم الاتفاق عليهم في الشات.</p>
            </div>
            <div className="grid grid-cols-2 gap-3 lg:grid-cols-3 xl:grid-cols-4">
              {products.map((product) => <ProductCard key={product.id} product={product} compact />)}
            </div>
          </section>
        )}

        {!loading && artisans.length === 0 && products.length === 0 && (
          <div className="mt-8 rounded-2xl border border-brand-100 bg-white p-8 text-center soft-shadow">
            <p className="text-lg font-black">لا توجد نتائج مناسبة</p>
            <p className="mt-2 text-sm text-stone-500">جرب فرعا آخر أو غير المركز من القائمة الجانبية.</p>
          </div>
        )}
      </div>
    </main>
  )
}
