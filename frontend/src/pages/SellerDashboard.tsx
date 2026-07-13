import { FormEvent, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { products as productsApi, sellers as sellersApi } from '../api'
import ArabicTimeSelect from '../components/ArabicTimeSelect'
import { findTrade, findTradeCategory, selectableTrades, trades } from '../data/trades'
import { queryClient } from '../lib/queryClient'
import { imageFallback } from '../utils/assets'

function listOf(response: any) {
  const value = response?.data?.data ?? response?.data ?? []
  return Array.isArray(value) ? value : []
}

function errorText(reason: any, fallback: string) {
  const value = reason?.error || reason?.response?.data?.error || reason?.response?.data
  return value ? JSON.stringify(value) : fallback
}

export default function SellerDashboard() {
  const [activeTab, setActiveTab] = useState<'overview' | 'products'>('overview')
  const [profile, setProfile] = useState<any>(null)
  const [products, setProducts] = useState<any[]>([])
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [image, setImage] = useState<File | null>(null)
  const [coverImage, setCoverImage] = useState<File | null>(null)
  const [profileImage, setProfileImage] = useState<File | null>(null)
  const [saving, setSaving] = useState(false)
  const [details, setDetails] = useState({
    name: '',
    food_description: '',
    pickup_address: '',
    experience_years: '0',
    is_open: true,
    work_start_time: '09:00',
    work_end_time: '17:00',
    professions: ['carpenter:doors-windows'],
  })
  const [newProduct, setNewProduct] = useState({
    name: '',
    description: '',
    price: '',
    trade: 'all',
    trade_category: 'all',
    is_available: true,
  })

  async function load() {
    setError('')
    try {
      const [profileResponse, productResponse] = await Promise.all([
        sellersApi.profile(),
        productsApi.sellerProducts(),
      ])
      const nextProfile = profileResponse.data.data
      setProfile(nextProfile)
      setDetails({
        name: nextProfile.name || '',
        food_description: nextProfile.food_description || '',
        pickup_address: nextProfile.pickup_address || '',
        experience_years: String(nextProfile.experience_years || 0),
        is_open: Boolean(nextProfile.is_open),
        work_start_time: (nextProfile.work_start_time || '09:00').slice(0, 5),
        work_end_time: (nextProfile.work_end_time || '17:00').slice(0, 5),
        professions: (nextProfile.professions || []).map((item: any) => `${item.trade}:${item.category}`),
      })
      setProducts(listOf(productResponse))
    } catch (reason: any) {
      setError(errorText(reason, 'تعذر تحميل لوحة العامل'))
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function updateDetails(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      const professions = details.professions.map((value) => {
        const [trade, category] = value.split(':')
        const tradeInfo = trades.find((item) => item.id === trade)
        const categoryInfo = tradeInfo?.categories.find((item) => item.id === category)
        return { trade, category, title: `${tradeInfo?.name || trade} - ${categoryInfo?.name || category}` }
      })
      const response = await sellersApi.updateProfile({
        name: details.name,
        food_description: details.food_description,
        pickup_address: details.pickup_address,
        experience_years: Number(details.experience_years),
        is_open: details.is_open,
        work_start_time: details.work_start_time,
        work_end_time: details.work_end_time,
        professions,
      })
      setProfile(response.data.data)
      await queryClient.invalidateQueries({ queryKey: ['chefs'] })
    } catch (reason: any) {
      setError(errorText(reason, 'تعذر تحديث بيانات العامل'))
    } finally {
      setSaving(false)
    }
  }

  async function updateImages(event: FormEvent) {
    event.preventDefault()
    if (!coverImage && !profileImage) return
    setSaving(true)
    setError('')
    try {
      const payload = new FormData()
      if (coverImage) payload.append('cover_image', coverImage)
      if (profileImage) payload.append('profile_image', profileImage)
      const response = await sellersApi.updateProfile(payload)
      setProfile(response.data.data)
      setCoverImage(null)
      setProfileImage(null)
    } catch (reason: any) {
      setError(errorText(reason, 'تعذر تحديث الصور'))
    } finally {
      setSaving(false)
    }
  }

  async function createProduct(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      const payload = new FormData()
      payload.append('name', newProduct.name)
      payload.append('description', newProduct.description)
      payload.append('ingredients', newProduct.description || 'معروض للبيع من العامل')
      payload.append('price', newProduct.price || '0')
      payload.append('listing_type', 'sale')
      payload.append('trade', newProduct.trade)
      payload.append('trade_category', newProduct.trade_category)
      payload.append('category', newProduct.trade_category)
      payload.append('preparation_time', '30')
      payload.append('is_available', String(newProduct.is_available))
      if (image) payload.append('image', image)
      await productsApi.create(payload)
      setShowForm(false)
      setImage(null)
      setNewProduct({ ...newProduct, name: '', description: '', price: '' })
      await queryClient.invalidateQueries({ queryKey: ['products'] })
      await load()
    } catch (reason: any) {
      setError(errorText(reason, 'تعذر إضافة المعروض'))
    } finally {
      setSaving(false)
    }
  }

  async function removeProduct(id: number) {
    if (!window.confirm('هل تريد حذف هذا المعروض؟')) return
    await productsApi.remove(id)
    await queryClient.invalidateQueries({ queryKey: ['products'] })
    await load()
  }

  const selectedTrade = useMemo(
    () => trades.find((item) => item.id === newProduct.trade) || trades[0],
    [newProduct.trade],
  )

  return (
    <main className="page-shell">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="eyebrow">إدارة حساب العامل</p>
          <h1 className="page-heading mt-1">لوحة العامل</h1>
          <p className="page-subtitle">{profile?.name || 'بياناتك ومعروضاتك في مكان واحد'}</p>
        </div>
        <Link to="/for-sale" className="secondary-button">صفحة للبيع</Link>
      </div>

      <div className="mt-5 flex gap-2 overflow-x-auto">
        {(['overview', 'products'] as const).map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)} className={`rounded-xl px-4 py-2.5 text-xs font-bold transition ${activeTab === tab ? 'bg-forest-800 text-white shadow-lg' : 'border border-[#ebe7df] bg-white text-stone-500'}`}>
            {tab === 'overview' ? 'البيانات' : 'للبيع'}
          </button>
        ))}
      </div>

      {error && <p className="mt-4 rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}

      {activeTab === 'overview' && (
        <section className="mt-5 space-y-4">
          <form onSubmit={updateDetails} className="surface-card grid gap-3 p-4">
            <h2 className="font-black">بياناتك ومهنك</h2>
            <div className="grid gap-3 rounded-2xl border border-stone-100 bg-white/70 p-3 sm:grid-cols-[1fr_1fr_1fr]">
              <label className="flex items-center justify-between gap-3 rounded-xl bg-white px-3 py-2 text-sm font-bold">
                <span>{details.is_open ? 'متاح الآن' : 'غير متاح الآن'}</span>
                <input type="checkbox" checked={details.is_open} onChange={(event) => setDetails({ ...details, is_open: event.target.checked })} className="h-5 w-5 accent-emerald-700" />
              </label>
              <label className="text-xs font-bold text-stone-600">
                يبدأ العمل
                <ArabicTimeSelect required value={details.work_start_time} onChange={(value) => setDetails({ ...details, work_start_time: value })} />
              </label>
              <label className="text-xs font-bold text-stone-600">
                ينتهي العمل
                <ArabicTimeSelect required value={details.work_end_time} onChange={(value) => setDetails({ ...details, work_end_time: value })} />
              </label>
            </div>
            <input required value={details.name} onChange={(event) => setDetails({ ...details, name: event.target.value })} placeholder="اسم العامل أو الورشة" className="field-control" />
            <textarea rows={3} value={details.food_description} onChange={(event) => setDetails({ ...details, food_description: event.target.value })} placeholder="نبذة عن شغلك وخبرتك" className="field-control" />
            <textarea required minLength={15} rows={2} value={details.pickup_address} onChange={(event) => setDetails({ ...details, pickup_address: event.target.value })} placeholder="عنوان شغلك بالتفصيل" className="field-control" />
            <input type="number" min="0" max="80" value={details.experience_years} onChange={(event) => setDetails({ ...details, experience_years: event.target.value })} placeholder="سنوات الخبرة" className="field-control" />
            <div className="grid max-h-60 gap-2 overflow-y-auto rounded-2xl bg-white/70 p-3 sm:grid-cols-2">
              {selectableTrades.flatMap((trade) => trade.categories.map((category) => {
                const value = `${trade.id}:${category.id}`
                return (
                  <label key={value} className="flex items-center gap-2 text-xs font-bold">
                    <input
                      type="checkbox"
                      checked={details.professions.includes(value)}
                      onChange={(event) => setDetails((current) => ({
                        ...current,
                        professions: event.target.checked
                          ? [...current.professions, value]
                          : current.professions.filter((item) => item !== value),
                      }))}
                      className="h-4 w-4 accent-forest-800"
                    />
                    {trade.icon} {trade.name} - {category.name}
                  </label>
                )
              }))}
            </div>
            <button disabled={saving} className="primary-button">{saving ? 'جاري الحفظ...' : 'حفظ البيانات'}</button>
          </form>

          <form onSubmit={updateImages} className="surface-card p-4">
            <h2 className="font-black">صور الحساب</h2>
            <p className="mt-1 text-xs text-stone-500">ارفع صورة غلاف وصورة شخصية واضحة للورشة أو العامل.</p>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <label className="rounded-xl border border-dashed border-stone-300 p-3 text-sm font-bold">
                صورة الغلاف
                <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={(event) => setCoverImage(event.target.files?.[0] || null)} className="mt-2 block w-full text-xs" />
              </label>
              <label className="rounded-xl border border-dashed border-stone-300 p-3 text-sm font-bold">
                الصورة الشخصية
                <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={(event) => setProfileImage(event.target.files?.[0] || null)} className="mt-2 block w-full text-xs" />
              </label>
            </div>
            <button disabled={saving || (!coverImage && !profileImage)} className="primary-button mt-3">حفظ الصور</button>
          </form>

          <div className="grid gap-3 sm:grid-cols-2">
            <Stat value={products.length} label="معروضات للبيع" />
            <Stat value={details.is_open ? 'متاح' : 'غير متاح'} label="حالة العامل" />
          </div>
        </section>
      )}

      {activeTab === 'products' && (
        <section className="mt-5 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-xl font-black text-forest-900">حاجاتك المعروضة للبيع</h2>
              <p className="text-sm text-stone-500">أي حاجة تضيفها هنا هتظهر في صفحة البيع حسب المركز والمهنة.</p>
            </div>
            <button onClick={() => setShowForm((value) => !value)} className="primary-button">
              {showForm ? 'إغلاق النموذج' : '+ إضافة حاجة للبيع'}
            </button>
          </div>

          {showForm && (
            <form onSubmit={createProduct} className="grid gap-3 rounded-2xl border border-orange-100 bg-white p-4 shadow-xl">
              <div className="grid gap-3 sm:grid-cols-2">
                <input required placeholder="اسم المعروض" value={newProduct.name} onChange={(event) => setNewProduct({ ...newProduct, name: event.target.value })} className="field-control" />
                <input type="number" min="0" step="1" placeholder="السعر بالجنيه، أو سيبه فاضي للاتفاق" value={newProduct.price} onChange={(event) => setNewProduct({ ...newProduct, price: event.target.value })} className="field-control" />
              </div>
              <textarea required rows={3} placeholder="وصف مختصر: الحالة، المقاس، الكمية، وطريقة الاستلام" value={newProduct.description} onChange={(event) => setNewProduct({ ...newProduct, description: event.target.value })} className="field-control" />
              <div className="grid gap-2 sm:grid-cols-2">
                <select value={newProduct.trade} onChange={(event) => {
                  const nextTrade = trades.find((item) => item.id === event.target.value) || trades[0]
                  setNewProduct({ ...newProduct, trade: nextTrade.id, trade_category: nextTrade.categories[0].id })
                }} className="field-control">
                  {trades.map((trade) => <option key={trade.id} value={trade.id}>{trade.name}</option>)}
                </select>
                <select value={newProduct.trade_category} onChange={(event) => setNewProduct({ ...newProduct, trade_category: event.target.value })} className="field-control">
                  {selectedTrade.categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
                </select>
              </div>
              <label className="flex items-center justify-between gap-3 rounded-xl bg-stone-50 px-3 py-2 text-sm font-bold">
                <span>{newProduct.is_available ? 'ظاهر ومتاح للبيع' : 'مخفي مؤقتا'}</span>
                <input type="checkbox" checked={newProduct.is_available} onChange={(event) => setNewProduct({ ...newProduct, is_available: event.target.checked })} className="h-5 w-5 accent-forest-800" />
              </label>
              <label className="rounded-xl border border-dashed border-orange-200 p-3 text-sm text-stone-600">
                صورة المعروض
                <input type="file" accept="image/jpeg,image/png,image/webp" onChange={(event) => setImage(event.target.files?.[0] || null)} className="mt-2 block w-full text-xs" />
              </label>
              <button disabled={saving} className="rounded-xl bg-stone-950 py-3 font-bold text-white disabled:bg-stone-500">
                {saving ? 'جاري النشر...' : 'حفظ ونشر المعروض'}
              </button>
            </form>
          )}

          {products.length === 0 && (
            <p className="surface-card p-8 text-center text-sm text-stone-500">
              لسه مفيش حاجات معروضة للبيع.
            </p>
          )}
          {products.map((product) => {
            const trade = findTrade(product.trade)
            const category = findTradeCategory(product.trade, product.trade_category || product.category)
            const price = Number(product.price || 0)
            return (
              <article key={product.id} className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-white/70 bg-white p-4 shadow-lg">
                <div className="flex min-w-0 items-center gap-3">
                  {product.image && <img src={product.image} alt="" onError={imageFallback} className="h-16 w-20 rounded-xl object-cover" />}
                  <div className="min-w-0">
                    <h2 className="font-black">{product.name}</h2>
                    <p className="text-sm text-stone-500">{trade.name} · {category.name} · {price > 0 ? `${price.toLocaleString('ar-EG')} جنيه` : 'السعر بالاتفاق'}</p>
                  </div>
                </div>
                <button onClick={() => removeProduct(product.id)} className="rounded-lg bg-rose-50 px-3 py-2 text-xs font-bold text-rose-700">حذف</button>
              </article>
            )
          })}
        </section>
      )}
    </main>
  )
}

function Stat({ value, label }: { value: string | number; label: string }) {
  return <div className="rounded-2xl bg-white p-5 shadow-lg"><p className="text-3xl font-black">{value}</p><p className="text-sm text-stone-500">{label}</p></div>
}
