import { useNavigate } from 'react-router-dom'
import { useMarkNotificationRead, useNotifications } from '../hooks/useMarketplace'

export default function Notifications() {
  const navigate = useNavigate()
  const notifications = useNotifications().data || []
  const markRead = useMarkNotificationRead()

  function openNotification(id: number, orderId?: string, type?: string) {
    markRead.mutate(id)
    if (orderId) navigate(`/chat/${orderId}`)
    else if (type === 'message') navigate('/support')
  }

  return (
    <main className="page-shell max-w-4xl">
      <p className="eyebrow">ابقَ على اطلاع</p>
      <h1 className="page-heading mt-1">الإشعارات</h1>
      <section className="mt-7 space-y-3">
        {notifications.map((item) => (
          <button key={item.id} onClick={() => openNotification(item.id, item.orderId, item.type)} className={`w-full rounded-2xl border p-5 text-right shadow-card transition hover:-translate-y-0.5 ${item.read ? 'border-[#ebe7df] bg-white' : 'border-brand-200 bg-brand-50'}`}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-black">{item.title}</p>
                <p className="mt-1 text-sm leading-6 text-stone-600">{item.content}</p>
                {item.orderId && <p className="mt-2 text-xs font-black text-brand-700">فتح الطلب والمحادثة ←</p>}
                {!item.orderId && item.type === 'message' && <p className="mt-2 text-xs font-black text-brand-700">فتح دعم صنعتى ←</p>}
              </div>
              {!item.read && <span className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full bg-rose-600" />}
            </div>
            <p className="mt-3 text-xs text-stone-400">{item.createdAt}</p>
          </button>
        ))}
      </section>
    </main>
  )
}

