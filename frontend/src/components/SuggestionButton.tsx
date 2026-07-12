import { FormEvent, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { auth } from '../api'
import { errorMessage } from '../services/response'
import { useAuthStore } from '../stores/authStore'
import { useUiStore } from '../stores/uiStore'

export default function SuggestionButton() {
  const profile = useAuthStore((state) => state.profile)
  const language = useUiStore((state) => state.language)
  const [open, setOpen] = useState(false)
  const [subject, setSubject] = useState('')
  const [message, setMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  if (!profile || !['user', 'seller'].includes(profile.role)) return null

  async function submit(event: FormEvent) {
    event.preventDefault()
    setSending(true)
    setFeedback(null)
    try {
      await auth.sendSuggestion({ subject, message })
      setSubject('')
      setMessage('')
      setFeedback({
        type: 'success',
        text: language === 'ar' ? 'تم إرسال اقتراحك بنجاح، شكرًا لك.' : 'Your suggestion was sent successfully. Thank you.',
      })
    } catch (error) {
      setFeedback({
        type: 'error',
        text: errorMessage(error, language === 'ar' ? 'تعذر إرسال الاقتراح' : 'Could not send your suggestion'),
      })
    } finally {
      setSending(false)
    }
  }

  return (
    <>
      <button
        type="button"
        onClick={() => { setOpen(true); setFeedback(null) }}
        className="fixed bottom-24 right-4 z-30 inline-flex items-center gap-2 rounded-full bg-brand-500 px-4 py-3 text-xs font-bold text-white shadow-float transition hover:-translate-y-0.5 hover:bg-brand-600 md:bottom-6 md:right-6"
      >
        <span aria-hidden="true">💡</span>
        {language === 'ar' ? 'اقتراح' : 'Suggestion'}
      </button>

      <AnimatePresence>
        {open && (
          <div className="fixed inset-0 z-[70] grid place-items-center p-4">
            <motion.button
              type="button"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setOpen(false)}
              className="absolute inset-0 bg-black/45 backdrop-blur-sm"
              aria-label={language === 'ar' ? 'إغلاق' : 'Close'}
            />
            <motion.div
              initial={{ opacity: 0, y: 20, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 15, scale: 0.98 }}
              role="dialog"
              aria-modal="true"
              aria-labelledby="suggestion-title"
              className="relative w-full max-w-lg rounded-3xl bg-white p-5 shadow-2xl"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 id="suggestion-title" className="text-xl font-black">
                    {language === 'ar' ? 'أرسل اقتراحك' : 'Send your suggestion'}
                  </h2>
                  <p className="mt-1 text-sm text-stone-500">
                    {language === 'ar' ? 'رأيك يساعدنا في تحسين المنصة.' : 'Your feedback helps us improve the marketplace.'}
                  </p>
                </div>
                <button type="button" onClick={() => setOpen(false)} className="grid h-9 w-9 place-items-center rounded-full bg-stone-100 text-xl">×</button>
              </div>

              <form onSubmit={submit} className="mt-5 space-y-3">
                <label className="block">
                  <span className="mb-1 block text-sm font-bold">{language === 'ar' ? 'العنوان' : 'Subject'}</span>
                  <input
                    required
                    minLength={3}
                    maxLength={160}
                    value={subject}
                    onChange={(event) => setSubject(event.target.value)}
                    className="w-full rounded-xl border border-orange-100 bg-orange-50/50 px-4 py-3 outline-none focus:border-brand-500"
                  />
                </label>
                <label className="block">
                  <span className="mb-1 block text-sm font-bold">{language === 'ar' ? 'تفاصيل الاقتراح' : 'Suggestion details'}</span>
                  <textarea
                    required
                    minLength={10}
                    maxLength={4000}
                    rows={5}
                    value={message}
                    onChange={(event) => setMessage(event.target.value)}
                    className="w-full resize-none rounded-xl border border-orange-100 bg-orange-50/50 px-4 py-3 outline-none focus:border-brand-500"
                  />
                </label>
                {feedback && (
                  <p className={`rounded-xl px-3 py-2 text-sm font-bold ${feedback.type === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'}`}>
                    {feedback.text}
                  </p>
                )}
                <button disabled={sending} className="w-full rounded-xl bg-stone-950 py-3 font-black text-white disabled:opacity-60">
                  {sending
                    ? language === 'ar' ? 'جارٍ الإرسال...' : 'Sending...'
                    : language === 'ar' ? 'إرسال الاقتراح' : 'Send suggestion'}
                </button>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  )
}
