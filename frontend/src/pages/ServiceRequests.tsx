import { FormEvent, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { orders } from '../api'
import { selectableTrades, trades } from '../data/trades'
import { useLocations } from '../hooks/useMarketplace'
import { errorMessage, listOf } from '../services/response'
import { useAuthStore } from '../stores/authStore'
import type { ServiceRequest } from '../types/marketplace'
import { imageFallback, mediaUrl } from '../utils/assets'

function mapServiceRequest(raw: any): ServiceRequest {
  return {
    id: Number(raw.id),
    title: raw.title || '',
    description: raw.description || '',
    governorate: raw.governorate || '',
    center: raw.center || '',
    trade: raw.trade || '',
    tradeCategory: raw.trade_category || '',
    status: raw.status || 'open',
    customerName: raw.customer_name || '',
    images: Array.isArray(raw.images)
      ? raw.images.map((item: any) => ({
        id: Number(item.id),
        image: mediaUrl(item.image, ''),
        sortOrder: Number(item.sort_order || 0),
        createdAt: item.created_at || '',
      }))
      : [],
    chatOrderIds: Array.isArray(raw.chat_order_ids) ? raw.chat_order_ids.map(Number) : [],
    createdAt: raw.created_at || '',
    updatedAt: raw.updated_at || '',
  }
}

export default function ServiceRequests() {
  const navigate = useNavigate()
  const profile = useAuthStore((state) => state.profile)
  const isWorker = profile?.role === 'seller'
  const locationsQuery = useLocations()
  const locations = locationsQuery.data || []
  const [items, setItems] = useState<ServiceRequest[]>([])
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [images, setImages] = useState<File[]>([])
  const [form, setForm] = useState({
    title: '',
    description: '',
    governorate: '',
    center: '',
    trade: '',
    trade_category: '',
  })

  const centers = useMemo(
    () => locations.find((item) => item.name_ar === form.governorate)?.centers || [],
    [form.governorate, locations],
  )
  const selectedTrade = useMemo(
    () => trades.find((item) => item.id === form.trade),
    [form.trade],
  )

  async function load() {
    setError('')
    try {
      const response = isWorker ? await orders.openServiceRequests() : await orders.serviceRequests()
      setItems(listOf<any>(response).map(mapServiceRequest))
    } catch (reason) {
      setError(errorMessage(reason, 'تعذر تحميل طلبات المشاكل'))
    }
  }

  useEffect(() => {
    load()
  }, [isWorker])

  async function submit(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      const payload = new FormData()
      Object.entries(form).forEach(([key, value]) => payload.append(key, value))
      images.forEach((image) => payload.append('images', image))
      await orders.createServiceRequest(payload)
      setForm({ title: '', description: '', governorate: '', center: '', trade: '', trade_category: '' })
      setImages([])
      await load()
    } catch (reason) {
      setError(errorMessage(reason, 'تعذر نشر طلب المشكلة'))
    } finally {
      setSaving(false)
    }
  }

  async function openChat(item: ServiceRequest) {
    setSaving(true)
    setError('')
    try {
      if (item.chatOrderIds[0]) {
        navigate(`/chat/${item.chatOrderIds[0]}`)
        return
      }
      const response = await orders.startServiceRequestChat(item.id)
      const orderId = response.data?.data?.order_id || response.data?.order_id
      navigate(`/chat/${orderId}`)
    } catch (reason) {
      setError(errorMessage(reason, 'تعذر فتح المحادثة'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <main className="page-shell pb-28">
      <div className="mb-5">
        <p className="eyebrow">{isWorker ? 'طلبات قريبة منك' : 'صور المشكلة'}</p>
        <h1 className="page-heading mt-1">
          {isWorker ? 'طلبات العملاء المفتوحة' : 'اطلب صنايعي للمشكلة'}
        </h1>
        <p className="page-subtitle">
          {isWorker
            ? 'شوف صور ووصف المشكلة وافتح شات مع العميل لو تقدر تساعده.'
            : 'ارفع صور المشكلة واكتب وصفها، والصنايعية المناسبين يقدروا يتواصلوا معاك.'}
        </p>
      </div>

      {error && <p className="mb-4 rounded-xl bg-rose-50 p-3 text-sm font-bold text-rose-700">{error}</p>}

      {!isWorker && (
        <form onSubmit={submit} className="surface-card mb-6 grid gap-3 p-4">
          <input
            required
            value={form.title}
            onChange={(event) => setForm({ ...form, title: event.target.value })}
            placeholder="عنوان المشكلة: تسريب حنفية، باب مكسور، تشطيب أوضة..."
            className="field-control"
          />
          <textarea
            required
            minLength={10}
            rows={4}
            value={form.description}
            onChange={(event) => setForm({ ...form, description: event.target.value })}
            placeholder="اكتب تفاصيل المشكلة والمكان وطبيعة الشغل المطلوب"
            className="field-control"
          />
          <div className="grid gap-2 sm:grid-cols-2">
            <select
              required
              value={form.governorate}
              onChange={(event) => setForm({ ...form, governorate: event.target.value, center: '' })}
              className="field-control"
            >
              <option value="">اختر المحافظة</option>
              {locations.map((item) => <option key={item.id} value={item.name_ar}>{item.name_ar}</option>)}
            </select>
            <select
              required
              value={form.center}
              disabled={!form.governorate}
              onChange={(event) => setForm({ ...form, center: event.target.value })}
              className="field-control"
            >
              <option value="">اختر المركز</option>
              {centers.map((item) => <option key={item.id} value={item.name_ar}>{item.name_ar}</option>)}
            </select>
          </div>
          <div className="grid gap-2 sm:grid-cols-2">
            <select
              value={form.trade}
              onChange={(event) => setForm({ ...form, trade: event.target.value, trade_category: '' })}
              className="field-control"
            >
              <option value="">مش عارف المهنة</option>
              {selectableTrades.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
            <select
              value={form.trade_category}
              disabled={!selectedTrade}
              onChange={(event) => setForm({ ...form, trade_category: event.target.value })}
              className="field-control"
            >
              <option value="">كل الفروع</option>
              {(selectedTrade?.categories || []).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
          </div>
          <label className="rounded-xl border border-dashed border-orange-200 p-3 text-sm font-bold text-stone-600">
            صور المشكلة
            <input
              type="file"
              multiple
              accept="image/jpeg,image/png,image/webp,image/gif"
              onChange={(event) => setImages(Array.from(event.target.files || []))}
              className="mt-2 block w-full text-xs"
            />
            {images.length > 0 && <span className="mt-2 block text-xs text-forest-800">{images.length.toLocaleString('ar-EG')} صور جاهزة</span>}
          </label>
          <button disabled={saving || locationsQuery.isLoading} className="primary-button">
            {saving ? 'جاري النشر...' : 'نشر طلب المشكلة'}
          </button>
        </form>
      )}

      <section className="grid gap-4 lg:grid-cols-2">
        {items.length === 0 && (
          <p className="surface-card p-8 text-center text-sm font-bold text-stone-500">
            {isWorker ? 'لا توجد طلبات مناسبة حاليا.' : 'لم تنشر أي طلبات بعد.'}
          </p>
        )}
        {items.map((item) => (
          <article key={item.id} className="overflow-hidden rounded-2xl border border-white/70 bg-white shadow-card">
            {item.images[0] && <img src={item.images[0].image} alt="" onError={imageFallback} className="h-56 w-full object-cover" />}
            <div className="p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h2 className="text-lg font-black text-forest-900">{item.title}</h2>
                  <p className="mt-1 text-xs font-bold text-stone-500">{item.governorate} - {item.center}</p>
                </div>
                <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-black text-emerald-700">مفتوح</span>
              </div>
              <p className="mt-3 text-sm leading-7 text-stone-600">{item.description}</p>
              {item.images.length > 1 && (
                <div className="mt-3 flex gap-2 overflow-x-auto pb-1">
                  {item.images.slice(1).map((image) => (
                    <img key={image.id} src={image.image} alt="" onError={imageFallback} className="h-16 w-20 shrink-0 rounded-xl object-cover" />
                  ))}
                </div>
              )}
              {isWorker && (
                <button type="button" disabled={saving} onClick={() => openChat(item)} className="primary-button mt-4 w-full">
                  {item.chatOrderIds[0] ? 'فتح المحادثة' : 'تواصل مع العميل'}
                </button>
              )}
              {!isWorker && item.chatOrderIds.length > 0 && (
                <button type="button" onClick={() => navigate(`/chat/${item.chatOrderIds[0]}`)} className="secondary-button mt-4 w-full">
                  فتح محادثة الصنايعي
                </button>
              )}
            </div>
          </article>
        ))}
      </section>
    </main>
  )
}
