import { FormEvent, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { auth } from '../api'
import ArabicTimeSelect from '../components/ArabicTimeSelect'
import { egyptGovernorates } from '../data/egyptLocations'
import { trades } from '../data/trades'
import { useLocations, useNotifications, useSellerApplication } from '../hooks/useMarketplace'
import { queryClient } from '../lib/queryClient'
import { errorMessage } from '../services/response'
import { useAuthStore } from '../stores/authStore'

function localLocations() {
  return egyptGovernorates.map((governorate, index) => ({
    id: index + 1,
    name_ar: governorate.name,
    centers: governorate.centers.map((center, centerIndex) => ({
      id: (index + 1) * 100 + centerIndex,
      name_ar: center,
    })),
  }))
}

export default function Profile() {
  const navigate = useNavigate()
  const { profile, refreshToken, logout, setProfile } = useAuthStore()
  const notifications = useNotifications().data || []
  const sellerApplication = useSellerApplication()
  const locationsQuery = useLocations()
  const fallbackLocations = useMemo(() => localLocations(), [])
  const locations = locationsQuery.data?.length ? locationsQuery.data : fallbackLocations
  const unreadNotifications = notifications.filter((item) => !item.read).length
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    name: '',
    governorate: '',
    center: '',
    description: '',
    address: '',
    age: '',
    nationalId: '',
    profession: 'carpenter:doors-windows',
    workStartTime: '09:00',
    workEndTime: '17:00',
  })
  const centers = locations.find((item) => item.name_ar === form.governorate)?.centers || []

  async function apply(event: FormEvent) {
    event.preventDefault()
    setError('')
    try {
      const [trade, category] = form.profession.split(':')
      await sellerApplication.mutateAsync({
        name: form.name,
        governorate: form.governorate,
        center: form.center,
        food_description: form.description,
        pickup_address: form.address,
        age: Number(form.age),
        national_id: form.nationalId,
        professions: [{ trade, category }],
        work_start_time: form.workStartTime,
        work_end_time: form.workEndTime,
      } as any)
      const response = await auth.profile()
      setProfile(response.data.data)
      setStatus('تم تفعيل حساب العامل. يمكنك إدارة بياناتك ومعروضاتك الآن.')
      window.setTimeout(() => navigate('/seller'), 700)
    } catch (reason: any) {
      setError(errorMessage(reason, 'تعذر إرسال الطلب'))
    }
  }

  async function signOut() {
    if (refreshToken) await auth.logout(refreshToken).catch(() => undefined)
    logout()
    queryClient.clear()
    navigate('/auth')
  }

  const displayName = [profile?.first_name, profile?.last_name].filter(Boolean).join(' ') || profile?.username

  return (
    <main className="page-shell max-w-5xl">
      <section className="rounded-2xl bg-stone-950 p-5 text-white soft-shadow">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="grid h-16 w-16 place-items-center rounded-2xl bg-white/10 text-2xl font-black">{displayName?.charAt(0) || 'م'}</div>
            <div>
              <h1 className="text-2xl font-black">مرحبا، {displayName}</h1>
              <p className="text-sm text-white/75">{profile?.email || profile?.username}</p>
            </div>
          </div>
          <button onClick={signOut} className="rounded-xl bg-white/10 px-3 py-2 text-xs font-bold">خروج</button>
        </div>
        <div className="mt-5 grid grid-cols-2 gap-2 text-center">
          <div className="rounded-xl bg-white/10 p-3"><p className="text-lg font-black">{unreadNotifications}</p><p className="text-xs text-white/75">تنبيهات</p></div>
          <div className="rounded-xl bg-white/10 p-3"><p className="text-lg font-black">{profile?.role === 'seller' ? 'عامل' : profile?.is_staff ? 'أدمن' : 'زبون'}</p><p className="text-xs text-white/75">نوع الحساب</p></div>
        </div>
      </section>

      {(profile?.role === 'seller' || profile?.is_staff) && (
        <section className="mt-5 grid grid-cols-2 gap-3">
          {profile?.role === 'seller' && <Link to="/seller" className="rounded-2xl bg-brand-500 p-4 text-center font-black text-white">لوحة العامل</Link>}
          {profile?.is_staff && <Link to="/admin" className="rounded-2xl bg-stone-950 p-4 text-center font-black text-white">لوحة الإدارة</Link>}
        </section>
      )}

      {profile?.role === 'user' && (
        <form onSubmit={apply} className="mt-5 rounded-2xl border border-[#dfe7e3] bg-white p-4 soft-shadow">
          <h2 className="text-lg font-black">التسجيل كعامل</h2>
          <p className="mt-1 text-sm leading-6 text-stone-500">اكتب بياناتك ومهنتك الأساسية ومواعيد العمل. العنوان التفصيلي إجباري.</p>
          <div className="mt-4 grid gap-3">
            <input required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="اسم العامل أو الورشة" className="field-control" />
            <div className="grid grid-cols-2 gap-2">
              <select required value={form.governorate} onChange={(event) => setForm({ ...form, governorate: event.target.value, center: '' })} className="field-control">
                <option value="">المحافظة</option>
                {locations.map((item) => <option key={item.id} value={item.name_ar}>{item.name_ar}</option>)}
              </select>
              <select required disabled={!form.governorate} value={form.center} onChange={(event) => setForm({ ...form, center: event.target.value })} className="field-control">
                <option value="">المركز</option>
                {centers.map((item) => <option key={item.id} value={item.name_ar}>{item.name_ar}</option>)}
              </select>
            </div>
            <select value={form.profession} onChange={(event) => setForm({ ...form, profession: event.target.value })} className="field-control">
              {trades.flatMap((trade) => trade.categories.map((category) => <option key={`${trade.id}:${category.id}`} value={`${trade.id}:${category.id}`}>{trade.name} - {category.name}</option>))}
            </select>
            <div className="grid grid-cols-2 gap-2">
              <input required type="number" min="18" max="80" value={form.age} onChange={(event) => setForm({ ...form, age: event.target.value })} placeholder="السن" className="field-control" />
              <input required inputMode="numeric" pattern="\d{14}" maxLength={14} value={form.nationalId} onChange={(event) => setForm({ ...form, nationalId: event.target.value })} placeholder="الرقم القومي" className="field-control" />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <label className="text-xs font-bold text-stone-600">يبدأ العمل<ArabicTimeSelect required value={form.workStartTime} onChange={(value) => setForm({ ...form, workStartTime: value })} /></label>
              <label className="text-xs font-bold text-stone-600">ينتهي العمل<ArabicTimeSelect required value={form.workEndTime} onChange={(value) => setForm({ ...form, workEndTime: value })} /></label>
            </div>
            <textarea required value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} placeholder="وصف شغلك وخبرتك" className="field-control min-h-24" />
            <textarea required minLength={15} value={form.address} onChange={(event) => setForm({ ...form, address: event.target.value })} placeholder="عنوان شغلك بالتفصيل" className="field-control min-h-20" />
            {status && <p className="rounded-xl bg-green-50 p-3 text-sm text-green-700">{status}</p>}
            {error && <p className="rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}
            <button disabled={sellerApplication.isPending} className="primary-button w-full">تفعيل حساب العامل</button>
          </div>
        </form>
      )}
    </main>
  )
}
