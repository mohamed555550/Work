import { motion } from 'framer-motion'
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import ProductCard from '../components/ProductCard'
import { useChef, useProducts, useStartChefChat } from '../hooks/useMarketplace'
import { useAuthStore } from '../stores/authStore'
import { errorMessage } from '../services/response'
import { imageFallback } from '../utils/assets'
import NotFound from './NotFound'

export default function ChefDetail() {
  const navigate = useNavigate()
  const id = Number(useParams().id)
  const authenticated = useAuthStore((state) => Boolean(state.accessToken))
  const [chatError, setChatError] = useState('')
  const workerQuery = useChef(id)
  const productsQuery = useProducts({ seller: id })
  const startChat = useStartChefChat()

  if (workerQuery.isLoading) return <main className="min-h-screen animate-pulse bg-orange-50/40" />
  if (!workerQuery.data) return <NotFound />

  const worker = workerQuery.data
  const products = productsQuery.data?.products || []
  const workGallery = worker.workGallery || []

  async function openChat() {
    setChatError('')
    if (!authenticated) return navigate('/auth')
    try {
      const conversation = await startChat.mutateAsync(worker.id)
      navigate(`/chat/${conversation.order_id}`)
    } catch (error: any) {
      setChatError(errorMessage(error?.response?.data, 'تعذر فتح المحادثة'))
    }
  }

  return (
    <main className="min-h-screen pb-28">
      <section className="relative">
        <div className="h-64 overflow-hidden bg-gradient-to-br from-forest-900 via-forest-800 to-brand-900 sm:h-80">
          {worker.coverImage && <img src={worker.coverImage} alt={`غلاف ${worker.name}`} onError={imageFallback} className="h-full w-full object-cover" />}
          <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/5 to-black/15" />
        </div>
        <div className="relative mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="-mt-16 flex items-end gap-4">
            <div className="h-32 w-32 shrink-0 overflow-hidden rounded-3xl border-[5px] border-white bg-brand-50 shadow-float sm:h-40 sm:w-40">
              {worker.profileImage ? <img src={worker.profileImage} alt={worker.name} onError={imageFallback} className="h-full w-full object-cover" /> : <span className="grid h-full w-full place-items-center text-4xl font-black text-brand-700">{worker.name.slice(0, 1)}</span>}
            </div>
            <div className="min-w-0 pb-3">
              <h1 className="truncate text-2xl font-black sm:text-4xl">{worker.name}</h1>
              <p className="mt-2 text-sm text-white drop-shadow">{worker.governorate} · {worker.center}</p>
            </div>
          </motion.div>
          <div className="mt-6 surface-card p-5">
            <h2 className="font-black">نبذة عن العامل</h2>
            <p className="mt-2 text-sm leading-7 text-stone-600">{worker.bio || 'لم يضف العامل نبذة بعد.'}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {worker.professions?.map((item, index) => <span key={`${item.trade}-${item.category}-${index}`} className="rounded-full bg-forest-50 px-3 py-1 text-xs font-black text-forest-800">{item.title || `${item.trade} - ${item.category}`}</span>)}
            </div>
          </div>
          <div className="fixed bottom-24 left-4 z-30 flex max-w-[calc(100vw-2rem)] flex-col items-start sm:bottom-6 sm:left-6">
            {chatError && <p className="mb-2 max-w-xs rounded-xl border border-rose-100 bg-white px-3 py-2 text-right text-sm font-bold text-rose-600 shadow-lg">{chatError}</p>}
            <button type="button" onClick={openChat} disabled={startChat.isPending} className="primary-button rounded-full">
              <span aria-hidden="true">💬</span>
              {startChat.isPending ? 'جاري فتح المحادثة...' : 'مراسلة العامل'}
            </button>
          </div>
        </div>
      </section>

      {workGallery.length > 0 && (
        <section className="mx-auto mt-10 max-w-6xl px-4 sm:px-6 lg:px-8">
          <p className="eyebrow">شغل سابق</p>
          <h2 className="mt-1 text-2xl font-extrabold text-forest-900">معرض شغل {worker.name}</h2>
          <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {workGallery.map((item) => (
              <article key={item.id} className="overflow-hidden rounded-2xl border border-[#e9e5de] bg-white shadow-card">
                <img src={item.image} alt={item.caption} onError={imageFallback} className="h-56 w-full object-cover" />
                <div className="p-4">
                  <p className="text-sm font-bold leading-7 text-stone-700">{item.caption}</p>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}

      <section className="mx-auto mt-10 max-w-6xl px-4 sm:px-6 lg:px-8">
        <p className="eyebrow">للبيع</p>
        <h2 className="mt-1 text-2xl font-extrabold text-forest-900">منتجات وخدمات العامل</h2>
        <div className="mt-5 grid grid-cols-2 gap-4 xl:grid-cols-3">
          {products.map((product) => <ProductCard key={product.id} product={product} />)}
        </div>
      </section>
    </main>
  )
}
