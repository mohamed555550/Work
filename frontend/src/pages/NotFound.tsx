import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <main className="grid min-h-screen place-items-center px-4 pb-24">
      <div className="surface-card max-w-md p-10 text-center">
        <p className="text-5xl font-black text-brand-500">404</p>
        <h1 className="mt-3 text-xl font-black">الصفحة غير موجودة</h1>
        <p className="mt-2 text-sm text-stone-500">الرابط غير صحيح أو تم نقله.</p>
        <Link to="/" className="primary-button mt-6">العودة للرئيسية</Link>
      </div>
    </main>
  )
}
