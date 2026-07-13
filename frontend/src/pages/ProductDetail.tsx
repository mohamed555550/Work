import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useChef, useFavorites, useProduct, useStartChefChat, useToggleFavorite } from '../hooks/useMarketplace'
import { findTrade, findTradeCategory } from '../data/trades'
import { useAuthStore } from '../stores/authStore'
import { formatArabicTime } from '../components/ChefCard'
import { imageFallback } from '../utils/assets'
import NotFound from './NotFound'

export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const token = useAuthStore((state) => state.accessToken)
  const productQuery = useProduct(Number(id))
  const favorites = useFavorites().data || []
  const toggleFavorite = useToggleFavorite()
  const startChat = useStartChefChat()
  const product = productQuery.data
  const workerQuery = useChef(Number(product?.sellerId))
  const [activeImage, setActiveImage] = useState('')

  const gallery = useMemo(() => {
    if (!product) return []
    return product.images?.length ? product.images : [product.image]
  }, [product])

  useEffect(() => {
    setActiveImage(gallery[0] || '')
  }, [gallery])

  if (productQuery.isLoading) return <main className="min-h-screen p-8 text-center">جاري تحميل المعروض...</main>
  if (!product) return <NotFound />

  const worker = workerQuery.data
  const isFavorite = favorites.some((item) => item.productId === product.id)
  const trade = product.trade ? findTrade(product.trade) : null
  const tradeCategory = product.trade ? findTradeCategory(product.trade, product.tradeCategory) : null
  const sellerId = product.sellerId
  const price = Number(product.price || 0)

  async function openChat() {
    if (!token) return navigate('/auth')
    const conversation = await startChat.mutateAsync(sellerId)
    navigate(`/chat/${conversation.order_id}`)
  }

  return (
    <main className="mx-auto min-h-screen max-w-6xl pb-28">
      <div className="relative h-80 overflow-hidden sm:mx-6 sm:mt-7 sm:rounded-[2rem] lg:h-[28rem]">
        <img src={activeImage || product.image} alt={product.name} onError={imageFallback} className="h-full w-full object-cover" />
        <div className="absolute inset-x-0 top-0 flex items-center justify-between p-4">
          <Link to="/for-sale" className="grid h-11 w-11 place-items-center rounded-full bg-white/90 font-black">‹</Link>
          <button onClick={() => token ? toggleFavorite.mutate(product.id) : navigate('/auth')} className="grid h-11 w-11 place-items-center rounded-full bg-white/90 text-rose-600">
            {isFavorite ? '♥' : '♡'}
          </button>
        </div>
      </div>

      {gallery.length > 1 && (
        <div className="mx-4 mt-3 flex gap-2 overflow-x-auto pb-2 sm:mx-10" dir="rtl">
          {gallery.map((image) => (
            <button
              key={image}
              type="button"
              onClick={() => setActiveImage(image)}
              className={`h-20 w-24 shrink-0 overflow-hidden rounded-2xl border-2 bg-white ${image === (activeImage || product.image) ? 'border-brand-500' : 'border-white'}`}
            >
              <img src={image} alt="" onError={imageFallback} className="h-full w-full object-cover" />
            </button>
          ))}
        </div>
      )}

      <section className="relative -mt-7 rounded-t-[2rem] border border-[#dfe7e3] bg-white px-5 pb-8 pt-7 shadow-card sm:mx-10 sm:rounded-[2rem] sm:px-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm font-bold text-brand-700">{worker?.name}</p>
            <h1 className="mt-1 text-3xl font-black leading-tight">{product.name}</h1>
          </div>
          <span className="rounded-full bg-forest-50 px-3 py-2 text-sm font-black text-forest-800">
            {price > 0 ? `${price.toLocaleString('ar-EG')} جنيه` : 'السعر بالاتفاق'}
          </span>
        </div>

        {trade && (
          <p className="mt-4 inline-flex rounded-full bg-forest-50 px-3 py-2 text-xs font-black text-forest-800">
            {trade.name}{tradeCategory ? ` - ${tradeCategory.name}` : ''}
          </p>
        )}

        <div className="mt-5 rounded-2xl border border-[#dfe7e3] bg-white p-4 soft-shadow">
          <h2 className="font-black">الوصف</h2>
          <p className="mt-2 text-sm leading-7 text-stone-600">{product.description || 'لا يوجد وصف إضافي.'}</p>
        </div>

        <div className="mt-4 rounded-2xl border border-[#dfe7e3] bg-white p-4 soft-shadow">
          <h2 className="font-black">عن العامل</h2>
          <p className="mt-2 text-sm leading-7 text-stone-600">{worker?.bio || 'لا توجد نبذة بعد.'}</p>
          <p className="mt-3 text-sm text-stone-600">
            <span className="font-black">المكان: </span>
            {worker?.pickupAddress || `${worker?.governorate || ''}، ${worker?.center || ''}`}
          </p>
          {worker && (
            <p className="mt-2 text-sm font-black text-stone-700">
              مواعيد العمل: من {formatArabicTime(worker.workStartTime)} إلى {formatArabicTime(worker.workEndTime)}
            </p>
          )}
        </div>
      </section>

      <div className="fixed inset-x-0 bottom-0 z-40 mx-auto max-w-screen-sm border-t border-[#dfe7e3] bg-white p-4">
        <button
          onClick={openChat}
          disabled={startChat.isPending}
          className="w-full rounded-2xl bg-brand-500 py-4 text-center text-sm font-black text-white disabled:bg-stone-500"
        >
          {startChat.isPending ? 'جاري فتح الشات...' : 'راسل العامل واتفق على المعروض'}
        </button>
      </div>
    </main>
  )
}
