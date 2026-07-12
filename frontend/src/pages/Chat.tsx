import { ChangeEvent, FormEvent, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  useChat,
  useConversations,
  useDeleteMessage,
  useSendMessage,
} from '../hooks/useMarketplace'
import { useOrderChatSocket } from '../hooks/useRealtime'
import { useAuthStore } from '../stores/authStore'
import type { ChatMessage } from '../types/marketplace'

const emojis = ['😀', '😂', '🥰', '😍', '😊', '🙏', '👏', '👍', '❤️', '🔥', '🎉', '😋', '🍲', '👨‍🍳', '👩‍🍳']

function timeLabel(value: string) {
  return new Intl.DateTimeFormat('ar-EG', {
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(value))
}

function statusLabel(message: ChatMessage) {
  if (message.status === 'seen') return '✓✓ شوهدت'
  if (message.status === 'delivered') return '✓✓ وصلت'
  return '✓ أُرسلت'
}

export default function Chat() {
  const { orderId = '' } = useParams()
  const [message, setMessage] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [emojiOpen, setEmojiOpen] = useState(false)
  const [replyTo, setReplyTo] = useState<ChatMessage | null>(null)
  const [attachment, setAttachment] = useState<{ file: File; type: 'image' | 'video'; url: string } | null>(null)
  const [activeMessage, setActiveMessage] = useState<number | null>(null)
  const typingTimer = useRef<number | undefined>(undefined)
  const messagesEnd = useRef<HTMLDivElement | null>(null)
  const imageInput = useRef<HTMLInputElement | null>(null)
  const videoInput = useRef<HTMLInputElement | null>(null)
  const profile = useAuthStore((state) => state.profile)
  const conversations = useConversations(search)
  const orderMessages = useChat(orderId).data || []
  const sendMessageRest = useSendMessage(orderId)
  const deleteMessage = useDeleteMessage(orderId)
  const socket = useOrderChatSocket(orderId)

  const selectedConversation = useMemo(
    () => conversations.data?.find((item) => item.orderId === orderId),
    [conversations.data, orderId],
  )

  useEffect(() => {
    const timer = window.setTimeout(() => setSearch(searchInput.trim()), 250)
    return () => window.clearTimeout(timer)
  }, [searchInput])

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' })
  }, [orderMessages.length, socket.typing])

  useEffect(() => () => {
    if (typingTimer.current) window.clearTimeout(typingTimer.current)
    if (attachment) URL.revokeObjectURL(attachment.url)
  }, [attachment])

  function handleTyping(value: string) {
    setMessage(value)
    socket.sendTyping(Boolean(value.trim()))
    if (typingTimer.current) window.clearTimeout(typingTimer.current)
    typingTimer.current = window.setTimeout(() => socket.sendTyping(false), 1000)
  }

  function chooseFile(event: ChangeEvent<HTMLInputElement>, type: 'image' | 'video') {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return
    if (attachment) URL.revokeObjectURL(attachment.url)
    setAttachment({ file, type, url: URL.createObjectURL(file) })
  }

  async function submit(event: FormEvent) {
    event.preventDefault()
    const text = message.trim()
    if ((!text && !attachment) || !orderId) return
    socket.sendTyping(false)
    if (!attachment && socket.sendMessage(text, replyTo?.id)) {
      setMessage('')
      setReplyTo(null)
      setEmojiOpen(false)
      return
    }
    await sendMessageRest.mutateAsync({
      message: text || undefined,
      image: attachment?.type === 'image' ? attachment.file : undefined,
      video: attachment?.type === 'video' ? attachment.file : undefined,
      replyTo: replyTo?.id,
    })
    if (attachment) URL.revokeObjectURL(attachment.url)
    setMessage('')
    setAttachment(null)
    setReplyTo(null)
    setEmojiOpen(false)
  }

  const otherOnline = socket.otherOnline ?? selectedConversation?.otherUser.isOnline ?? false

  return (
    <main className="mx-auto my-0 grid h-[calc(100vh-116px)] max-w-7xl overflow-hidden bg-white lg:my-5 lg:h-[calc(100vh-156px)] lg:grid-cols-[22rem_1fr] lg:rounded-3xl lg:border lg:border-[#e9e5de] lg:shadow-card">
      <aside className={`${orderId ? 'hidden lg:flex' : 'flex'} min-h-0 flex-col border-l border-[#ebe7df] bg-white`}>
        <div className="border-b border-orange-100 p-4">
          <h1 className="text-2xl font-black">الرسائل</h1>
          <label className="mt-3 block">
            <span className="sr-only">البحث في المحادثات</span>
            <input
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="ابحث بالاسم أو الرسالة..."
              className="field-control"
            />
          </label>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto">
          {conversations.isLoading && <p className="p-5 text-sm text-stone-500">جارٍ تحميل المحادثات...</p>}
          {!conversations.isLoading && conversations.data?.length === 0 && (
            <p className="p-8 text-center text-sm text-stone-500">لا توجد محادثات مطابقة.</p>
          )}
          {conversations.data?.map((conversation) => (
            <Link
              key={conversation.id}
              to={`/chat/${conversation.orderId}`}
              className={`flex gap-3 border-b border-orange-50 p-4 transition hover:bg-orange-50/60 ${
                conversation.orderId === orderId ? 'bg-brand-50' : ''
              }`}
            >
              <div className="relative h-12 w-12 shrink-0 overflow-hidden rounded-full bg-orange-100">
                {conversation.otherUser.profileImage ? (
                  <img src={conversation.otherUser.profileImage} alt="" className="h-full w-full object-cover" />
                ) : (
                  <span className="grid h-full w-full place-items-center font-black text-brand-700">{conversation.otherUser.name.slice(0, 1)}</span>
                )}
                <span className={`absolute bottom-0 left-0 h-3.5 w-3.5 rounded-full border-2 border-white ${conversation.otherUser.isOnline ? 'bg-emerald-500' : 'bg-stone-300'}`} />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-2">
                  <h2 className="truncate font-black">{conversation.otherUser.name}</h2>
                  {conversation.lastMessage && <time className="text-[10px] text-stone-400">{timeLabel(conversation.lastMessage.createdAt)}</time>}
                </div>
                <div className="mt-1 flex items-center justify-between gap-2">
                  <p className="truncate text-xs text-stone-500">
                    {conversation.lastMessage?.messageType === 'image' ? '📷 صورة'
                      : conversation.lastMessage?.messageType === 'video' ? '🎥 فيديو'
                        : conversation.lastMessage?.message || 'ابدأ المحادثة'}
                  </p>
                  {conversation.unreadCount > 0 && <span className="grid min-h-5 min-w-5 place-items-center rounded-full bg-brand-500 px-1 text-[10px] font-black text-white">{conversation.unreadCount}</span>}
                </div>
              </div>
            </Link>
          ))}
        </div>
      </aside>

      <section className={`${orderId ? 'flex' : 'hidden lg:flex'} min-h-0 flex-col bg-[#f8f6f2]`}>
        {!orderId ? (
          <div className="grid flex-1 place-items-center text-center text-stone-500">
            <div><span className="text-5xl">💬</span><p className="mt-3 font-bold">اختر محادثة لبدء المراسلة</p></div>
          </div>
        ) : (
          <>
            <header className="z-20 flex items-center gap-3 border-b border-orange-100 bg-white/95 p-3 backdrop-blur">
              <Link to="/messages" className="grid h-10 w-10 place-items-center rounded-full bg-orange-50 font-black lg:hidden">‹</Link>
              <div className="relative h-11 w-11 overflow-hidden rounded-full bg-orange-100">
                {selectedConversation?.otherUser.profileImage ? (
                  <img src={selectedConversation.otherUser.profileImage} alt="" className="h-full w-full object-cover" />
                ) : (
                  <span className="grid h-full w-full place-items-center font-black text-brand-700">{selectedConversation?.otherUser.name.slice(0, 1) || 'م'}</span>
                )}
              </div>
              <div>
                <h1 className="font-black">{selectedConversation?.otherUser.name || 'محادثة الطلب'}</h1>
                <p className={`text-xs ${otherOnline ? 'text-emerald-600' : 'text-stone-400'}`}>
                  {socket.typing ? 'يكتب الآن...' : otherOnline ? 'متصل الآن' : 'غير متصل'}
                </p>
              </div>
              <span className={`mr-auto rounded-full px-2.5 py-1 text-[10px] font-bold ${socket.connected ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}`}>
                {socket.connected ? 'مباشر' : 'جارٍ الاتصال'}
              </span>
            </header>

            <div className="min-h-0 flex-1 space-y-3 overflow-y-auto px-4 py-5 sm:px-6">
              {orderMessages.map((item) => {
                const mine = item.senderId === profile?.id
                return (
                  <div key={item.id} className={`group flex ${mine ? 'justify-start' : 'justify-end'}`}>
                    <div className="relative max-w-[82%] sm:max-w-[68%]">
                      <button
                        type="button"
                        onClick={() => setActiveMessage(activeMessage === item.id ? null : item.id)}
                        aria-label="خيارات الرسالة"
                        className="absolute -left-8 top-2 hidden h-7 w-7 place-items-center rounded-full bg-white text-stone-400 shadow group-hover:grid"
                      >
                        •••
                      </button>
                      {activeMessage === item.id && (
                        <div className="absolute bottom-full left-0 z-10 mb-1 flex whitespace-nowrap rounded-xl border border-orange-100 bg-white p-1 text-xs shadow-xl">
                          {!item.isDeleted && <button type="button" onClick={() => { setReplyTo(item); setActiveMessage(null) }} className="rounded-lg px-3 py-2 hover:bg-orange-50">رد</button>}
                          <button type="button" onClick={() => deleteMessage.mutate({ id: item.id, scope: 'me' })} className="rounded-lg px-3 py-2 hover:bg-orange-50">حذف لديّ</button>
                          {mine && item.canDeleteForEveryone && <button type="button" onClick={() => deleteMessage.mutate({ id: item.id, scope: 'everyone' })} className="rounded-lg px-3 py-2 text-rose-600 hover:bg-rose-50">حذف للجميع</button>}
                        </div>
                      )}
                      <div className={`overflow-hidden rounded-2xl text-sm leading-6 ${mine ? 'rounded-tr-md bg-brand-500 text-white' : 'rounded-tl-md bg-white text-stone-700 shadow-sm'}`}>
                        {item.isDeleted ? (
                          <p className="px-4 py-3 italic opacity-70">تم حذف هذه الرسالة</p>
                        ) : (
                          <>
                            {item.reply && (
                              <div className={`mx-2 mt-2 rounded-xl border-r-4 px-3 py-2 text-xs ${mine ? 'border-white/70 bg-black/10' : 'border-brand-400 bg-orange-50'}`}>
                                <strong className="block">{item.reply.senderName}</strong>
                                <span className="line-clamp-1 opacity-80">{item.reply.message || (item.reply.messageType === 'image' ? 'صورة' : 'فيديو')}</span>
                              </div>
                            )}
                            {item.image && <img src={item.image} alt="صورة مرسلة" loading="lazy" className="max-h-80 w-full object-cover" />}
                            {item.video && <video src={item.video} controls preload="metadata" className="max-h-56 w-full bg-black object-contain sm:max-h-64" />}
                            {item.message && <p className="px-4 py-3">{item.message}</p>}
                          </>
                        )}
                      </div>
                      <div className={`mt-1 flex gap-2 text-[10px] text-stone-400 ${mine ? 'justify-start' : 'justify-end'}`}>
                        <time>{timeLabel(item.createdAt)}</time>
                        {mine && <span>{statusLabel(item)}</span>}
                      </div>
                    </div>
                  </div>
                )
              })}
              {socket.typing && (
                <div className="flex justify-end">
                  <div className="rounded-2xl rounded-tl-md bg-white px-4 py-2 text-stone-400 shadow-sm">•••</div>
                </div>
              )}
              <div ref={messagesEnd} />
            </div>

            <form onSubmit={submit} className="border-t border-orange-100 bg-white p-3 pb-20 sm:pb-3">
              {replyTo && (
                <div className="mb-2 flex items-center justify-between rounded-xl border-r-4 border-brand-500 bg-orange-50 px-3 py-2 text-xs">
                  <div><strong>رد على {replyTo.senderName}</strong><p className="mt-0.5 max-w-md truncate text-stone-500">{replyTo.message || 'وسائط'}</p></div>
                  <button type="button" onClick={() => setReplyTo(null)} className="text-lg">×</button>
                </div>
              )}
              {attachment && (
                <div className="mb-2 relative w-fit overflow-hidden rounded-xl bg-stone-950">
                  {attachment.type === 'image'
                    ? <img src={attachment.url} alt="معاينة" className="h-24 w-28 object-cover" />
                    : <video src={attachment.url} className="h-24 w-32 object-cover" />}
                  <button type="button" onClick={() => { URL.revokeObjectURL(attachment.url); setAttachment(null) }} className="absolute left-1 top-1 grid h-6 w-6 place-items-center rounded-full bg-black/60 text-white">×</button>
                </div>
              )}
              {emojiOpen && (
                <div className="mb-2 flex flex-wrap gap-1 rounded-2xl border border-orange-100 bg-white p-2 shadow-xl">
                  {emojis.map((emoji) => <button type="button" key={emoji} onClick={() => handleTyping(message + emoji)} className="grid h-9 w-9 place-items-center rounded-lg text-xl hover:bg-orange-50">{emoji}</button>)}
                </div>
              )}
              <div className="flex items-end gap-2">
                <input ref={imageInput} type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={(event) => chooseFile(event, 'image')} className="hidden" />
                <input ref={videoInput} type="file" accept="video/mp4,video/webm,video/quicktime" onChange={(event) => chooseFile(event, 'video')} className="hidden" />
                <button type="button" onClick={() => imageInput.current?.click()} className="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-orange-50" aria-label="إرسال صورة">📷</button>
                <button type="button" onClick={() => videoInput.current?.click()} className="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-orange-50" aria-label="إرسال فيديو">🎥</button>
                <button type="button" onClick={() => setEmojiOpen(!emojiOpen)} className="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-orange-50" aria-label="اختيار رمز تعبيري">😊</button>
                <textarea
                  value={message}
                  onChange={(event) => handleTyping(event.target.value)}
                  placeholder="اكتب رسالة..."
                  rows={1}
                  className="max-h-28 min-h-11 min-w-0 flex-1 resize-none rounded-2xl border border-orange-100 bg-orange-50 px-4 py-2.5 outline-none focus:border-brand-500"
                />
                <button disabled={sendMessageRest.isPending || (!message.trim() && !attachment)} className="h-11 rounded-xl bg-forest-800 px-5 text-sm font-bold text-white transition hover:bg-forest-700 disabled:opacity-40">إرسال</button>
              </div>
              <p className="mt-2 text-center text-[10px] font-semibold text-stone-400">
                يمكن للعامل والزبون تبادل أرقام الهاتف داخل المحادثة عند الحاجة.
              </p>
            </form>
          </>
        )}
      </section>
    </main>
  )
}

