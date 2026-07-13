import { motion } from 'framer-motion'
import { Link, useNavigate } from 'react-router-dom'
import { useFavorites, useStartChefChat, useToggleFavorite } from '../hooks/useMarketplace'
import { findTrade, findTradeCategory } from '../data/trades'
import { useAuthStore } from '../stores/authStore'
import { imageFallback } from '../utils/assets'
import type { Product } from '../types/marketplace'

interface ProductCardProps {
  product: Product
  compact?: boolean
}

export default function ProductCard({ product, compact = false }: ProductCardProps) {
  const navigate = useNavigate()
  const token = useAuthStore((state) => state.accessToken)
  const favorites = useFavorites().data || []
  const toggleFavorite = useToggleFavorite()
  const startChat = useStartChefChat()
  const isFavorite = favorites.some((item) => item.productId === product.id)
  const trade = product.trade ? findTrade(product.trade) : null
  const tradeCategory = product.trade ? findTradeCategory(product.trade, product.tradeCategory) : null
  const price = Number(product.price || 0)
  const showPrice = product.listingType === 'sale'

  async function openChat() {
    if (!token) return navigate('/auth')
    const conversation = await startChat.mutateAsync(product.sellerId)
    navigate(`/chat/${conversation.order_id}`)
  }

  return (
    <motion.article whileHover={{ y: -2 }} className="flex h-full flex-col overflow-hidden rounded-3xl border border-[#dfe4ee] bg-white shadow-card transition-shadow hover:shadow-float">
      <Link to={`/products/${product.id}`} className="relative overflow-hidden">
        <img src={product.image} alt={product.name} loading="lazy" onError={imageFallback} className={`w-full object-cover transition duration-500 hover:scale-105 ${compact ? 'h-40' : 'h-48'}`} />
        <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-black/35 to-transparent" />
        <button
          aria-label="تبديل المفضلة"
          onClick={(event) => {
            event.preventDefault()
            if (!token) return navigate('/auth')
            toggleFavorite.mutate(product.id)
          }}
          className={`absolute right-3 top-3 flex h-9 w-9 items-center justify-center rounded-xl border shadow-sm backdrop-blur-md transition ${isFavorite ? 'border-rose-200 bg-rose-50/90 text-rose-600' : 'border-white/60 bg-white/90 text-stone-500 hover:text-rose-600'}`}
        >
          {isFavorite ? '♥' : '♡'}
        </button>
      </Link>
      <div className="flex flex-1 flex-col p-4">
        <Link to={`/products/${product.id}`} className="mb-2">
          <p className="text-[10px] font-bold text-brand-600">
            {trade ? `${trade.name}${tradeCategory ? ` - ${tradeCategory.name}` : ''}` : 'معروض للبيع'}
          </p>
          <h3 className="mt-1.5 line-clamp-2 text-base font-extrabold leading-6 text-forest-900">{product.name}</h3>
        </Link>
        <p className="mb-3 line-clamp-2 text-xs leading-5 text-stone-500">{product.description}</p>
        <div className="mt-auto space-y-2">
          <div className="flex items-center justify-between gap-2 text-xs">
            <span className="truncate text-stone-500">{product.sellerName}</span>
            {showPrice && (
              <span className="shrink-0 font-black text-forest-800">
                {price > 0 ? `${price.toLocaleString('ar-EG')} جنيه` : 'السعر بالاتفاق'}
              </span>
            )}
          </div>
          <button
            disabled={startChat.isPending}
            onClick={openChat}
            className="flex w-full items-center justify-center rounded-xl bg-forest-800 px-3.5 py-2.5 text-xs font-bold text-white transition hover:bg-forest-700 disabled:cursor-not-allowed disabled:bg-stone-500 disabled:opacity-100"
          >
            {startChat.isPending ? 'جاري فتح الشات...' : 'راسل العامل واتفق'}
          </button>
        </div>
      </div>
    </motion.article>
  )
}
