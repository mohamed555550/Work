import { FormEvent, useEffect, useMemo, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { support as supportApi } from '../api'
import { dataOf, errorMessage, listOf } from '../services/response'
import { useAuthStore } from '../stores/authStore'
import type { SupportConversation, SupportMessage } from '../types/marketplace'

function mapMessage(raw: any): SupportMessage {
  return {
    id: Number(raw.id),
    sender: Number(raw.sender),
    senderName: raw.sender_name,
    isSupport: Boolean(raw.is_support),
    message: raw.message,
    readAt: raw.read_at || null,
    createdAt: raw.created_at,
  }
}

function mapConversation(raw: any): SupportConversation {
  return {
    id: Number(raw.id),
    user: Number(raw.user),
    userName: raw.user_name,
    userEmail: raw.user_email,
    userRole: raw.user_role,
    status: raw.status,
    unreadCount: Number(raw.unread_count || 0),
    lastMessage: raw.last_message ? mapMessage(raw.last_message) : null,
    messages: (raw.messages || []).map(mapMessage),
    createdAt: raw.created_at,
    updatedAt: raw.updated_at,
  }
}

function timeLabel(value: string) {
  return new Intl.DateTimeFormat('ar-EG', {
    day: 'numeric',
    month: 'short',
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(value))
}

const quickMessages = [
  'أريد تقديم شكوى بخصوص طلب',
  'محتاج مساعدة في استخدام الموقع',
  'لدي مشكلة في حسابي',
]

export default function SupportChat() {
  const profile = useAuthStore((state) => state.profile)
  const isAdmin = Boolean(profile?.is_staff || profile?.role === 'admin')
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [message, setMessage] = useState('')
  const [search, setSearch] = useState('')
  const [feedback, setFeedback] = useState('')
  const messagesEnd = useRef<HTMLDivElement | null>(null)
  const queryClient = useQueryClient()

  const conversations = useQuery({
    queryKey: ['support-conversations', search],
    enabled: isAdmin,
    refetchInterval: 5000,
    queryFn: async () => listOf<any>(await supportApi.conversations(search)).map(mapConversation),
  })

  const conversation = useQuery({
    queryKey: ['support-conversation', isAdmin ? selectedId : 'mine'],
    enabled: !isAdmin || Boolean(selectedId),
    refetchInterval: 4000,
    queryFn: async () => mapConversation(dataOf<any>(
      isAdmin && selectedId
        ? await supportApi.detail(selectedId)
        : await supportApi.mine(),
    )),
  })

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation.data?.messages.length])

  const sendMessage = useMutation({
    mutationFn: (text: string) => supportApi.send(text, isAdmin ? selectedId || undefined : undefined),
    onSuccess: async () => {
      setMessage('')
      setFeedback('')
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['support-conversation'] }),
        queryClient.invalidateQueries({ queryKey: ['support-conversations'] }),
      ])
    },
    onError: (reason) => setFeedback(errorMessage(reason, 'تعذر إرسال الرسالة')),
  })

  const updateStatus = useMutation({
    mutationFn: (status: 'open' | 'closed') => supportApi.updateStatus(selectedId!, status),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['support-conversation'] }),
        queryClient.invalidateQueries({ queryKey: ['support-conversations'] }),
      ])
    },
  })

  const selected = conversation.data
  const title = isAdmin && selected ? selected.userName : 'دعم صنعتى'
  const subtitle = isAdmin && selected
    ? `${selected.userRole === 'seller' ? 'عامل' : 'زبون'} · ${selected.userEmail}`
    : 'موجودون لمساعدتك واستقبال شكواك'

  const sortedConversations = useMemo(
    () => conversations.data || [],
    [conversations.data],
  )

  function submit(event: FormEvent) {
    event.preventDefault()
    const text = message.trim()
    if (!text || (isAdmin && !selectedId)) return
    sendMessage.mutate(text)
  }

  return (
    <main className="mx-auto my-4 grid h-[calc(100vh-145px)] max-w-6xl overflow-hidden rounded-3xl border border-[#e8e3da] bg-white/95 text-[#1d2624] shadow-2xl backdrop-blur-xl lg:grid-cols-[20rem_1fr]">
      {isAdmin && (
        <aside className={`${selectedId ? 'hidden lg:flex' : 'flex'} min-h-0 flex-col border-l border-[#e8e3da] bg-[#f8f6f2]`}>
          <div className="border-b border-[#e8e3da] p-4">
            <h1 className="text-xl font-black">رسائل دعم صنعتى</h1>
            <p className="mt-1 text-xs text-stone-500">شكاوى واستفسارات الزبائن والعمال</p>
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="ابحث بالاسم أو البريد..."
              className="mt-4 w-full rounded-xl border border-[#d8d1c7] bg-white px-4 py-3 text-sm text-stone-800 outline-none placeholder:text-stone-400 focus:border-brand-400"
            />
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto">
            {sortedConversations.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => setSelectedId(item.id)}
                className={`flex w-full gap-3 border-b border-[#ebe7df] p-4 text-right transition hover:bg-white ${selectedId === item.id ? 'bg-brand-50' : ''}`}
              >
                <span className="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-forest-800 font-black text-white">
                  {item.userName.slice(0, 1)}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="flex items-center justify-between gap-2">
                    <b className="truncate">{item.userName}</b>
                    {item.unreadCount > 0 && <span className="grid min-w-5 place-items-center rounded-full bg-brand-500 px-1 text-[10px]">{item.unreadCount}</span>}
                  </span>
                  <span className="mt-1 block truncate text-xs text-stone-500">{item.lastMessage?.message || 'محادثة جديدة'}</span>
                </span>
              </button>
            ))}
            {!conversations.isLoading && sortedConversations.length === 0 && (
              <p className="p-8 text-center text-sm text-stone-500">لا توجد رسائل دعم حاليًا.</p>
            )}
          </div>
        </aside>
      )}

      <section className={`${isAdmin && !selectedId ? 'hidden lg:flex' : 'flex'} min-h-0 flex-col bg-[#fbfaf8]`}>
        {isAdmin && !selectedId ? (
          <div className="grid flex-1 place-items-center text-center text-stone-500">
            <div><span className="text-5xl">💬</span><p className="mt-3">اختر محادثة للرد عليها</p></div>
          </div>
        ) : (
          <>
            <header className="flex items-center gap-3 border-b border-[#e8e3da] bg-white/95 p-4">
              {isAdmin && (
                <button type="button" onClick={() => setSelectedId(null)} className="grid h-10 w-10 place-items-center rounded-full bg-stone-100 lg:hidden">‹</button>
              )}
              <span className="grid h-12 w-12 place-items-center rounded-full bg-forest-800 text-lg font-black text-white">A</span>
              <div>
                <h1 className="font-black">{title}</h1>
                <p className="text-xs text-stone-500">{subtitle}</p>
              </div>
              {isAdmin && selected && (
                <button
                  type="button"
                  onClick={() => updateStatus.mutate(selected.status === 'open' ? 'closed' : 'open')}
                  className="mr-auto rounded-full border border-[#e8e3da] bg-[#f7f4ef] px-3 py-2 text-xs font-bold"
                >
                  {selected.status === 'open' ? 'إغلاق الشكوى' : 'إعادة فتحها'}
                </button>
              )}
            </header>

            <div className="min-h-0 flex-1 space-y-3 overflow-y-auto px-4 py-5 sm:px-6">
              {!isAdmin && selected?.messages.length === 0 && (
                <div className="mx-auto max-w-lg rounded-2xl border border-[#e8e3da] bg-white p-5 text-center shadow-sm">
                  <h2 className="font-black">أهلًا بك في دعم صنعتى</h2>
                  <p className="mt-2 text-sm leading-6 text-stone-500">اكتب استفسارك أو شكواك وسيتمكن فريق إدارة الموقع فقط من رؤيتها والرد عليها.</p>
                  <div className="mt-4 flex flex-wrap justify-center gap-2">
                    {quickMessages.map((text) => (
                      <button key={text} type="button" onClick={() => setMessage(text)} className="rounded-full border border-[#e8e3da] bg-[#f7f4ef] px-3 py-2 text-xs hover:bg-brand-50">
                        {text}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {selected?.messages.map((item) => {
                const mine = item.sender === profile?.id
                return (
                  <div key={item.id} className={`flex ${mine ? 'justify-start' : 'justify-end'}`}>
                    <div className={`max-w-[82%] rounded-2xl px-4 py-3 text-sm leading-6 ${mine ? 'rounded-tr-md bg-brand-500 text-white' : 'rounded-tl-md bg-white text-stone-700 shadow-sm'}`}>
                      <p className="mb-1 text-[10px] font-bold opacity-60">{item.senderName}</p>
                      <p className="whitespace-pre-wrap">{item.message}</p>
                      <time className="mt-1 block text-[9px] opacity-50">{timeLabel(item.createdAt)}</time>
                    </div>
                  </div>
                )
              })}
              <div ref={messagesEnd} />
            </div>

            <form onSubmit={submit} className="border-t border-[#e8e3da] bg-white p-3 pb-20 sm:pb-3">
              {feedback && <p className="mb-2 rounded-xl bg-rose-950/60 px-3 py-2 text-xs text-rose-200">{feedback}</p>}
              <div className="flex items-end gap-2">
                <textarea
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                  placeholder={isAdmin ? 'اكتب رد دعم صنعتى...' : 'اكتب استفسارك أو شكواك...'}
                  rows={1}
                  maxLength={4000}
                  className="max-h-32 min-h-12 min-w-0 flex-1 resize-none rounded-2xl border border-[#d8d1c7] bg-[#fbfaf8] px-4 py-3 text-sm text-stone-800 outline-none placeholder:text-stone-400 focus:border-brand-400"
                />
                <button
                  disabled={sendMessage.isPending || !message.trim()}
                  className="h-12 rounded-xl bg-forest-800 px-6 text-sm font-black text-white transition hover:bg-forest-700 disabled:opacity-40"
                >
                  إرسال
                </button>
              </div>
              <p className="mt-2 text-center text-[10px] text-stone-400">المحادثة خاصة بينك وبين إدارة صنعتى.</p>
            </form>
          </>
        )}
      </section>
    </main>
  )
}

