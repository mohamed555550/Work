import ProductCard from '../components/ProductCard'
import { useFavorites, useProducts } from '../hooks/useMarketplace'

export default function Favorites() {
  const products = useProducts().data?.products || []
  const favorites = useFavorites().data || []
  const favoriteProducts = products.filter((product) => favorites.some((item) => item.productId === product.id))

  return (
    <main className="page-shell">
      <p className="eyebrow">اختياراتك المحفوظة</p>
      <h1 className="page-heading mt-1">المفضلة</h1>
      <p className="page-subtitle">منتجات وخدمات محفوظة للرجوع إليها لاحقا.</p>
      <section className="mt-7 grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-4">
        {favoriteProducts.length ? favoriteProducts.map((product) => <ProductCard key={product.id} product={product} />) : (
          <div className="surface-card col-span-full p-10 text-center">
            <p className="text-lg font-black">لا توجد عناصر في المفضلة</p>
            <p className="mt-2 text-sm text-stone-500">اضغط على القلب داخل أي منتج لحفظه هنا.</p>
          </div>
        )}
      </section>
    </main>
  )
}
