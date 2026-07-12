import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { auditLogs as auditApi, auth, products as productsApi, sellers as sellersApi } from '../api'
import { imageFallback } from '../utils/assets'

type Tab = 'overview' | 'users' | 'workers' | 'products' | 'audit'

function listOf(response: any) {
  const value = response?.data?.data ?? response?.data ?? []
  return Array.isArray(value) ? value : []
}

function timeLabel(value?: string) {
  if (!value) return '--:--'
  return value.slice(0, 5)
}

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<Tab>('overview')
  const [users, setUsers] = useState<any[]>([])
  const [workers, setWorkers] = useState<any[]>([])
  const [products, setProducts] = useState<any[]>([])
  const [logs, setLogs] = useState<any[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const openWorkers = useMemo(() => workers.filter((worker) => worker.is_open).length, [workers])

  async function load() {
    setLoading(true)
    setError('')
    try {
      const [userResponse, workerResponse, productResponse, auditResponse] = await Promise.all([
        auth.adminUsers(),
        sellersApi.pending(),
        productsApi.adminProducts(),
        auditApi.list(),
      ])
      setUsers(listOf(userResponse))
      setWorkers(listOf(workerResponse))
      setProducts(listOf(productResponse))
      setLogs(listOf(auditResponse))
    } catch (reason: any) {
      setError(reason?.error || 'تعذر تحميل لوحة الإدارة')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function updateUser(id: number, payload: Record<string, unknown>) {
    await auth.adminUpdateUser(id, payload)
    await load()
  }

  async function deleteUser(id: number) {
    if (!window.confirm('هل تريد حذف هذا المستخدم؟')) return
    await auth.adminDeleteUser(id)
    await load()
  }

  async function deleteProduct(id: number) {
    if (!window.confirm('هل تريد حذف هذا المنتج؟')) return
    await productsApi.remove(id)
    await load()
  }

  async function approveWorker(id: number, approved: 'approved' | 'rejected') {
    await sellersApi.approve(id, approved)
    await load()
  }

  return (
    <main className="page-shell">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="eyebrow">تحكم كامل</p>
          <h1 className="page-heading mt-1">لوحة الإدارة</h1>
          <p className="page-subtitle">إدارة المستخدمين والعمال والمنتجات وسجل النظام من مكان واحد.</p>
        </div>
        <div className="flex gap-2">
          <button onClick={load} className="secondary-button">{loading ? 'تحديث...' : 'تحديث'}</button>
          <Link to="/" className="primary-button">الواجهة الرئيسية</Link>
        </div>
      </div>

      <div className="mt-5 flex gap-2 overflow-x-auto pb-1">
        {[
          ['overview', 'نظرة عامة'],
          ['users', 'المستخدمون'],
          ['workers', 'العمال'],
          ['products', 'المنتجات'],
          ['audit', 'السجل'],
        ].map(([tab, label]) => (
          <button key={tab} onClick={() => setActiveTab(tab as Tab)} className={`shrink-0 rounded-xl px-4 py-2 text-sm font-bold ${activeTab === tab ? 'bg-stone-950 text-white' : 'bg-white text-stone-600'}`}>
            {label}
          </button>
        ))}
      </div>

      {error && <p className="mt-4 rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}

      {activeTab === 'overview' && (
        <section className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <Stat value={users.length} label="مستخدم" />
          <Stat value={workers.length} label="عامل" />
          <Stat value={openWorkers} label="عمال متاحين" />
          <Stat value={products.length} label="منتج" />
        </section>
      )}

      {activeTab === 'users' && (
        <section className="mt-5 grid gap-3">
          {users.map((user) => (
            <article key={user.id} className="surface-card flex flex-wrap items-center justify-between gap-3 p-4">
              <div>
                <h2 className="font-black">{user.first_name || user.username} {user.last_name || ''}</h2>
                <p className="text-sm text-stone-500">{user.email} · {user.role} · {user.is_active === false ? 'معطل' : 'نشط'}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <button onClick={() => updateUser(user.id, { role: 'user' })} className="secondary-button">زبون</button>
                <button onClick={() => updateUser(user.id, { role: 'seller' })} className="secondary-button">عامل</button>
                <button onClick={() => updateUser(user.id, { role: 'admin' })} className="secondary-button">أدمن</button>
                <button onClick={() => updateUser(user.id, { is_active: user.is_active === false })} className="rounded-xl bg-amber-100 px-4 py-2 text-sm font-bold text-amber-800">
                  {user.is_active === false ? 'تفعيل' : 'تعطيل'}
                </button>
                <button onClick={() => deleteUser(user.id)} className="rounded-xl bg-rose-100 px-4 py-2 text-sm font-bold text-rose-700">حذف</button>
              </div>
            </article>
          ))}
        </section>
      )}

      {activeTab === 'workers' && (
        <section className="mt-5 grid gap-3">
          {workers.map((worker) => (
            <article key={worker.id} className="surface-card flex flex-wrap items-center justify-between gap-3 p-4">
              <div>
                <h2 className="font-black">{worker.name}</h2>
                <p className="text-sm text-stone-500">{worker.governorate} · {worker.center} · {worker.approved}</p>
                <p className="mt-1 text-xs font-bold text-stone-500">
                  {worker.is_open ? 'متاح' : 'غير متاح'} · من {timeLabel(worker.work_start_time)} إلى {timeLabel(worker.work_end_time)}
                </p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => approveWorker(worker.id, 'approved')} className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-bold text-white">اعتماد</button>
                <button onClick={() => approveWorker(worker.id, 'rejected')} className="rounded-xl bg-rose-600 px-4 py-2 text-sm font-bold text-white">رفض</button>
              </div>
            </article>
          ))}
        </section>
      )}

      {activeTab === 'products' && (
        <section className="mt-5 grid gap-3">
          {products.map((product) => (
            <article key={product.id} className="surface-card flex flex-wrap items-center justify-between gap-3 p-4">
              <div className="flex items-center gap-3">
                {product.image && <img src={product.image} alt="" onError={imageFallback} className="h-16 w-20 rounded-xl object-cover" />}
                <div>
                  <h2 className="font-black">{product.name}</h2>
                  <p className="text-sm text-stone-500">{product.seller?.name} · الاتفاق في الشات · {product.listing_type}</p>
                </div>
              </div>
              <button onClick={() => deleteProduct(product.id)} className="rounded-xl bg-rose-100 px-4 py-2 text-sm font-bold text-rose-700">حذف</button>
            </article>
          ))}
        </section>
      )}

      {activeTab === 'audit' && (
        <section className="mt-5 grid gap-2">
          {logs.map((log) => (
            <article key={log.id} className="rounded-xl border border-white/60 bg-white/90 p-3 text-sm">
              <div className="flex justify-between gap-3"><b>{log.action}</b><span>{new Date(log.created_at).toLocaleString('ar-EG')}</span></div>
              <p className="text-stone-500">{log.user_name || 'النظام'} · {log.object_type} #{log.object_id}</p>
            </article>
          ))}
        </section>
      )}
    </main>
  )
}

function Stat({ value, label }: { value: string | number; label: string }) {
  return (
    <div className="surface-card p-5">
      <p className="text-3xl font-black text-forest-900">{value}</p>
      <p className="mt-1 text-sm font-bold text-stone-500">{label}</p>
    </div>
  )
}
