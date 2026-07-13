import { ChangeEvent, FormEvent, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { auth } from '../api'
import ArabicTimeSelect from '../components/ArabicTimeSelect'
import { egyptGovernorates } from '../data/egyptLocations'
import { selectableTrades as trades } from '../data/trades'
import { useLocations, useNotifications, useSellerApplication } from '../hooks/useMarketplace'
import { queryClient } from '../lib/queryClient'
import { errorMessage } from '../services/response'
import { useAuthStore } from '../stores/authStore'
import { imageFallback, mediaUrl } from '../utils/assets'

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
  const [profileImage, setProfileImage] = useState<File | null>(null)
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
      setStatus('طھظ… طھظپط¹ظٹظ„ ط­ط³ط§ط¨ ط§ظ„ط¹ط§ظ…ظ„. ظٹظ…ظƒظ†ظƒ ط¥ط¯ط§ط±ط© ط¨ظٹط§ظ†ط§طھظƒ ظˆظ…ط¹ط±ظˆط¶ط§طھظƒ ط§ظ„ط¢ظ†.')
      window.setTimeout(() => navigate('/seller'), 700)
    } catch (reason: any) {
      setError(errorMessage(reason, 'طھط¹ط°ط± ط¥ط±ط³ط§ظ„ ط§ظ„ط·ظ„ط¨'))
    }
  }

  async function signOut() {
    if (refreshToken) await auth.logout(refreshToken).catch(() => undefined)
    logout()
    queryClient.clear()
    navigate('/auth')
  }

  async function updateProfileImage(event: FormEvent) {
    event.preventDefault()
    if (!profileImage) return
    setError('')
    try {
      const payload = new FormData()
      payload.append('profile_image', profileImage)
      const response = await auth.updateProfile(payload)
      setProfile(response.data.data)
      setProfileImage(null)
      setStatus('طھظ… طھط­ط¯ظٹط« ط§ظ„طµظˆط±ط© ط§ظ„ط´ط®طµظٹط©')
    } catch (reason: any) {
      setError(errorMessage(reason, 'طھط¹ط°ط± طھط­ط¯ظٹط« ط§ظ„طµظˆط±ط© ط§ظ„ط´ط®طµظٹط©'))
    }
  }

  function chooseProfileImage(event: ChangeEvent<HTMLInputElement>) {
    setProfileImage(event.target.files?.[0] || null)
  }

  const displayName = [profile?.first_name, profile?.last_name].filter(Boolean).join(' ') || profile?.username

  return (
    <main className="page-shell max-w-5xl">
      <section className="rounded-2xl bg-stone-950 p-5 text-white soft-shadow">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="grid h-16 w-16 place-items-center overflow-hidden rounded-2xl bg-white/10 text-2xl font-black">
              {profile?.profile_image ? (
                <img src={mediaUrl(profile.profile_image, '')} alt={displayName} onError={imageFallback} className="h-full w-full object-cover" />
              ) : (
                displayName?.charAt(0) || 'م'
              )}
            </div>
            <div>
              <h1 className="text-2xl font-black">ظ…ط±ط­ط¨ط§طŒ {displayName}</h1>
              <p className="text-sm text-white/75">{profile?.email || profile?.username}</p>
            </div>
          </div>
          <button onClick={signOut} className="rounded-xl bg-white/10 px-3 py-2 text-xs font-bold">ط®ط±ظˆط¬</button>
        </div>
        <div className="mt-5 grid grid-cols-2 gap-2 text-center">
          <div className="rounded-xl bg-white/10 p-3"><p className="text-lg font-black">{unreadNotifications}</p><p className="text-xs text-white/75">طھظ†ط¨ظٹظ‡ط§طھ</p></div>
          <div className="rounded-xl bg-white/10 p-3"><p className="text-lg font-black">{profile?.role === 'seller' ? 'ط¹ط§ظ…ظ„' : profile?.is_staff ? 'ط£ط¯ظ…ظ†' : 'ط²ط¨ظˆظ†'}</p><p className="text-xs text-white/75">ظ†ظˆط¹ ط§ظ„ط­ط³ط§ط¨</p></div>
        </div>
      </section>

      <form onSubmit={updateProfileImage} className="mt-5 rounded-2xl border border-[#dfe7e3] bg-white p-4 soft-shadow">
        <h2 className="text-lg font-black">الصورة الشخصية</h2>
        <p className="mt-1 text-sm text-stone-500">ارفع صورة تظهر في حسابك والهيدر والمحادثات.</p>
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={chooseProfileImage} className="field-control max-w-md" />
          <button disabled={!profileImage} className="primary-button">حفظ الصورة</button>
        </div>
      </form>

      {(profile?.role === 'seller' || profile?.is_staff) && (
        <section className="mt-5 grid grid-cols-2 gap-3">
          {profile?.role === 'seller' && <Link to="/seller" className="rounded-2xl bg-brand-500 p-4 text-center font-black text-white">ظ„ظˆط­ط© ط§ظ„ط¹ط§ظ…ظ„</Link>}
          {profile?.is_staff && <Link to="/admin" className="rounded-2xl bg-stone-950 p-4 text-center font-black text-white">ظ„ظˆط­ط© ط§ظ„ط¥ط¯ط§ط±ط©</Link>}
        </section>
      )}

      {profile?.role === 'user' && (
        <form onSubmit={apply} className="mt-5 rounded-2xl border border-[#dfe7e3] bg-white p-4 soft-shadow">
          <h2 className="text-lg font-black">ط§ظ„طھط³ط¬ظٹظ„ ظƒط¹ط§ظ…ظ„</h2>
          <p className="mt-1 text-sm leading-6 text-stone-500">ط§ظƒطھط¨ ط¨ظٹط§ظ†ط§طھظƒ ظˆظ…ظ‡ظ†طھظƒ ط§ظ„ط£ط³ط§ط³ظٹط© ظˆظ…ظˆط§ط¹ظٹط¯ ط§ظ„ط¹ظ…ظ„. ط§ظ„ط¹ظ†ظˆط§ظ† ط§ظ„طھظپطµظٹظ„ظٹ ط¥ط¬ط¨ط§ط±ظٹ.</p>
          <div className="mt-4 grid gap-3">
            <input required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="ط§ط³ظ… ط§ظ„ط¹ط§ظ…ظ„ ط£ظˆ ط§ظ„ظˆط±ط´ط©" className="field-control" />
            <div className="grid grid-cols-2 gap-2">
              <select required value={form.governorate} onChange={(event) => setForm({ ...form, governorate: event.target.value, center: '' })} className="field-control">
                <option value="">ط§ظ„ظ…ط­ط§ظپط¸ط©</option>
                {locations.map((item) => <option key={item.id} value={item.name_ar}>{item.name_ar}</option>)}
              </select>
              <select required disabled={!form.governorate} value={form.center} onChange={(event) => setForm({ ...form, center: event.target.value })} className="field-control">
                <option value="">ط§ظ„ظ…ط±ظƒط²</option>
                {centers.map((item) => <option key={item.id} value={item.name_ar}>{item.name_ar}</option>)}
              </select>
            </div>
            <select value={form.profession} onChange={(event) => setForm({ ...form, profession: event.target.value })} className="field-control">
              {trades.flatMap((trade) => trade.categories.map((category) => <option key={`${trade.id}:${category.id}`} value={`${trade.id}:${category.id}`}>{trade.name} - {category.name}</option>))}
            </select>
            <div className="grid grid-cols-2 gap-2">
              <input required type="number" min="18" max="80" value={form.age} onChange={(event) => setForm({ ...form, age: event.target.value })} placeholder="ط§ظ„ط³ظ†" className="field-control" />
              <input required inputMode="numeric" pattern="\d{14}" maxLength={14} value={form.nationalId} onChange={(event) => setForm({ ...form, nationalId: event.target.value })} placeholder="ط§ظ„ط±ظ‚ظ… ط§ظ„ظ‚ظˆظ…ظٹ" className="field-control" />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <label className="text-xs font-bold text-stone-600">ظٹط¨ط¯ط£ ط§ظ„ط¹ظ…ظ„<ArabicTimeSelect required value={form.workStartTime} onChange={(value) => setForm({ ...form, workStartTime: value })} /></label>
              <label className="text-xs font-bold text-stone-600">ظٹظ†طھظ‡ظٹ ط§ظ„ط¹ظ…ظ„<ArabicTimeSelect required value={form.workEndTime} onChange={(value) => setForm({ ...form, workEndTime: value })} /></label>
            </div>
            <textarea required value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} placeholder="ظˆطµظپ ط´ط؛ظ„ظƒ ظˆط®ط¨ط±طھظƒ" className="field-control min-h-24" />
            <textarea required minLength={15} value={form.address} onChange={(event) => setForm({ ...form, address: event.target.value })} placeholder="ط¹ظ†ظˆط§ظ† ط´ط؛ظ„ظƒ ط¨ط§ظ„طھظپطµظٹظ„" className="field-control min-h-20" />
            {status && <p className="rounded-xl bg-green-50 p-3 text-sm text-green-700">{status}</p>}
            {error && <p className="rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}
            <button disabled={sellerApplication.isPending} className="primary-button w-full">طھظپط¹ظٹظ„ ط­ط³ط§ط¨ ط§ظ„ط¹ط§ظ…ظ„</button>
          </div>
        </form>
      )}
    </main>
  )
}

