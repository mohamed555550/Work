import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import ChefCard from '../components/ChefCard'
import ProductCard from '../components/ProductCard'
import { findTrade, findTradeCategory } from '../data/trades'
import { useChefs, useProducts } from '../hooks/useMarketplace'
import { useUiStore } from '../stores/uiStore'

const steps = [
  { number: '1', title: 'اختار الصنعة', description: 'حدد المحافظة والمركز والمهنة المطلوبة من القائمة الجانبية.' },
  { number: '2', title: 'راجع الكروت', description: 'شوف مهنة العامل، عنوانه، حالته، ومواعيد شغله من الساعة كام للساعة كام.' },
  { number: '3', title: 'افتح شات واتفق', description: 'اتكلموا على الميعاد، هل العامل هيروح للعميل ولا العميل هيروح له، وأي تفاصيل أو أرقام عادي.' },
]

export default function Home() {
  const { governorate, center, trade, tradeCategory, setSidebarOpen } = useUiStore()
  const selectedTrade = findTrade(trade)
  const selectedCategory = findTradeCategory(trade, tradeCategory)
  const workersQuery = useChefs({ governorate, center, trade, trade_category: tradeCategory })
  const productsQuery = useProducts({ governorate, center, listing_type: 'sale' })
  const workers = workersQuery.data || []
  const products = productsQuery.data?.products || []

  return (
    <main className="overflow-hidden bg-transparent">
      <section className="relative min-h-[600px] overflow-hidden lg:min-h-[670px]">
        <div className="absolute inset-0 bg-gradient-to-r from-white/5 via-black/5 to-black/30" />
        <div className="relative mx-auto flex min-h-[600px] max-w-[1500px] items-center justify-end px-5 py-20 sm:px-10 lg:min-h-[670px] lg:px-16">
          <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.65 }} className="max-w-xl rounded-[2rem] border border-white/70 bg-[#f8f3e9]/88 p-7 text-right shadow-[0_24px_80px_rgba(20,16,10,0.28)] backdrop-blur-lg sm:p-10">
            <span className="inline-flex items-center gap-2 rounded-full bg-[#e4f0bc] px-4 py-2 text-xs font-extrabold text-[#355515]">
              <span className="h-2 w-2 rounded-full bg-[#75a928]" /> صنايعية قريبين منك
            </span>
            <h1 className="mt-6 text-4xl font-extrabold leading-[1.35] text-[#242424] sm:text-5xl lg:text-[3.5rem]">
              اختار العامل المناسب<br /><span className="mt-2 inline-block text-[#547f18]">وافتح شات للاتفاق</span>
            </h1>
            <p className="mt-5 max-w-lg text-base font-bold leading-8 text-stone-600 sm:text-lg">
              تبحث الآن عن {selectedTrade.name} - {selectedCategory.name} في {center}، {governorate}.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/search" className="rounded-md bg-[#242424] px-7 py-3.5 text-sm font-extrabold text-white shadow-lg transition hover:-translate-y-0.5 hover:bg-[#547f18]">ابدأ البحث</Link>
              <button type="button" onClick={() => setSidebarOpen(true)} className="rounded-md border-2 border-[#6f982d] bg-[#e4f0bc] px-7 py-3 text-sm font-extrabold text-[#355515] shadow-md transition hover:-translate-y-0.5 hover:border-[#547f18] hover:bg-[#547f18] hover:text-white hover:shadow-lg">غير المهنة أو المركز</button>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="border-y border-white/50 bg-white/55 backdrop-blur-md">
        <div className="mx-auto grid max-w-6xl grid-cols-1 divide-y divide-stone-200 px-5 sm:grid-cols-3 sm:divide-x sm:divide-x-reverse sm:divide-y-0">
          <Stat value="+20" label="مهنة أساسية" />
          <Stat value="20" label="صورة خلفية واقعية" />
          <Stat value="شات" label="للاتفاق المباشر" />
        </div>
      </section>

      <section className="bg-[#fff1dc]/65 px-5 py-20 backdrop-blur-[2px] sm:px-8 lg:py-24">
        <div className="mx-auto max-w-6xl">
          <div className="mx-auto max-w-2xl text-center">
            <p className="eyebrow">ببساطة</p>
            <h2 className="mt-3 text-3xl font-extrabold text-[#242424] sm:text-4xl">الخدمة في 3 خطوات</h2>
          </div>
          <div className="mt-12 grid gap-5 md:grid-cols-3">
            {steps.map((step) => (
              <article key={step.number} className="rounded-2xl border border-white/70 bg-white/85 p-8 text-center shadow-lg">
                <span className="mx-auto grid h-10 w-10 place-items-center rounded-full bg-[#e3efbb] text-sm font-black text-[#4e7318]">{step.number}</span>
                <h3 className="mt-5 text-xl font-extrabold text-[#242424]">{step.title}</h3>
                <p className="mt-3 text-sm leading-7 text-stone-500">{step.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-[#edf5df]/65 px-5 py-20 backdrop-blur-[2px] sm:px-8 lg:py-24">
        <div className="mx-auto max-w-6xl">
          <div className="flex flex-wrap items-end justify-between gap-5">
            <div>
              <p className="eyebrow">عمال قريبين</p>
              <h2 className="mt-3 text-3xl font-extrabold text-[#242424] sm:text-4xl">{selectedTrade.name} في {center}</h2>
            </div>
            <Link to="/chefs" className="border-b-2 border-[#547f18] pb-1 text-sm font-extrabold text-[#426711]">شوف كل العمال ←</Link>
          </div>
          {!workersQuery.isLoading && workers.length > 0 && <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-3">{workers.slice(0, 3).map((worker, index) => <ChefCard key={worker.id} chef={worker} index={index} />)}</div>}
        </div>
      </section>

      <section className="bg-[#dcebc5]/65 px-5 py-20 backdrop-blur-[2px] sm:px-8 lg:py-24">
        <div className="mx-auto max-w-6xl">
          <div className="flex flex-wrap items-end justify-between gap-5">
            <div>
              <p className="eyebrow">للبيع</p>
              <h2 className="mt-3 text-3xl font-extrabold text-[#242424] sm:text-4xl">منتجات معروضة في مركزك</h2>
            </div>
            <Link to="/for-sale" className="border-b-2 border-[#547f18] pb-1 text-sm font-extrabold text-[#426711]">صفحة البيع ←</Link>
          </div>
          {!productsQuery.isLoading && products.length > 0 && <div className="mt-10 grid grid-cols-2 gap-3 lg:grid-cols-4">{products.slice(0, 4).map((product) => <ProductCard key={product.id} product={product} compact />)}</div>}
        </div>
      </section>
    </main>
  )
}

function Stat({ value, label }: { value: string; label: string }) {
  return <div className="px-6 py-7 text-center"><strong className="block text-2xl font-extrabold text-[#242424]">{value}</strong><span className="text-xs font-semibold text-stone-500">{label}</span></div>
}
