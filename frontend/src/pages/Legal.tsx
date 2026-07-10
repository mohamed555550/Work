import { Link } from 'react-router-dom'
import type { ReactNode } from 'react'

function LegalPage({ title, children }: { title: string; children: ReactNode }) {
  return (
    <main className="page-shell max-w-4xl">
      <div className="surface-card p-6 sm:p-10">
        <Link to="/" className="text-sm font-bold text-brand-700">العودة للرئيسية</Link>
        <h1 className="mt-4 text-3xl font-black text-stone-900">{title}</h1>
        <p className="mt-2 text-xs text-stone-500">آخر تحديث: 8 يوليو 2026</p>
        <div className="mt-7 space-y-6 text-sm leading-8 text-stone-700">{children}</div>
      </div>
    </main>
  )
}

export function Terms() {
  return (
    <LegalPage title="شروط الاستخدام">
      <section><h2 className="text-lg font-black">طبيعة المنصة</h2><p>المنصة تربط الزبائن بالعمال والصنايعية القريبين منهم حسب المحافظة والمركز والمهنة.</p></section>
      <section><h2 className="text-lg font-black">الحسابات والمحتوى</h2><p>يلتزم المستخدم بصحة بياناته، ويلتزم العامل بوصف خدماته ومنتجاته ومهاراته بدقة. يحق للإدارة تعطيل أو حذف الحسابات والمحتوى المخالف.</p></section>
      <section><h2 className="text-lg font-black">الاتفاق والدفع</h2><p>الاتفاق على التفاصيل والموعد وطريقة الدفع يتم بين الزبون والعامل عبر المحادثة أو التواصل المباشر.</p></section>
      <section><h2 className="text-lg font-black">التواصل</h2><p>يمكن للعامل والزبون تبادل أرقام الهاتف داخل الشات عند الحاجة لإتمام الخدمة.</p></section>
    </LegalPage>
  )
}

export function Privacy() {
  return (
    <LegalPage title="سياسة الخصوصية">
      <section><h2 className="text-lg font-black">البيانات التي نجمعها</h2><p>نجمع بيانات الحساب والموقع المختار والمهن والمنتجات والطلبات والمحادثات لتشغيل الخدمة.</p></section>
      <section><h2 className="text-lg font-black">الصور</h2><p>عند رفع صور للشغل أو المنتجات أو الحساب، يتم ضغطها وتقليل حجمها تلقائيا لتحسين سرعة التطبيق.</p></section>
      <section><h2 className="text-lg font-black">الرقم القومي</h2><p>عند تسجيل العامل لا نخزن الرقم القومي كاملًا؛ نحتفظ ببصمة رقمية وآخر أربعة أرقام لمنع تكرار الحساب.</p></section>
      <section><h2 className="text-lg font-black">حقوقك</h2><p>يمكنك طلب تعديل بياناتك أو حذف حسابك من خلال الدعم أو الإدارة.</p></section>
    </LegalPage>
  )
}
