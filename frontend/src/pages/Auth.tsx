import { useEffect, useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import { z } from 'zod'
import { auth } from '../api'
import ArabicTimeSelect from '../components/ArabicTimeSelect'
import { egyptGovernorates } from '../data/egyptLocations'
import { trades } from '../data/trades'
import { useLocations } from '../hooks/useMarketplace'
import { dataOf, errorMessage } from '../services/response'
import { useAuthStore } from '../stores/authStore'
import type { Session } from '../types/marketplace'

const loginSchema = z.object({
  username: z.string().min(3, 'اسم المستخدم مطلوب'),
  password: z.string().min(8, 'كلمة المرور لا تقل عن 8 أحرف'),
})

const registerSchema = z.object({
  username: z.string().min(3, 'اسم المستخدم لا يقل عن 3 أحرف').max(150),
  email: z.email('أدخل بريدًا إلكترونيًا صحيحًا'),
  first_name: z.string().min(2, 'الاسم الأول مطلوب'),
  last_name: z.string().min(2, 'اسم العائلة مطلوب'),
  password: z.string().min(8, 'كلمة المرور لا تقل عن 8 أحرف'),
  password_confirm: z.string(),
}).refine((value) => value.password === value.password_confirm, {
  path: ['password_confirm'],
  message: 'كلمتا المرور غير متطابقتين',
})

const workerRegisterSchema = registerSchema.and(z.object({
  kitchen_name: z.string().min(3, 'اكتب اسم العامل أو الورشة').max(180),
  governorate: z.string().min(1, 'اختر المحافظة'),
  center: z.string().min(1, 'اختر المركز'),
  age: z.string().regex(/^\d+$/, 'أدخل السن بشكل صحيح').refine((value) => {
    const age = Number(value)
    return age >= 18 && age <= 80
  }, 'السن يجب أن يكون بين 18 و80 سنة'),
  national_id: z.string().regex(/^\d{14}$/, 'الرقم القومي يجب أن يكون 14 رقمًا'),
  profession_trade: z.string().min(1, 'اختيار المهنة إجباري'),
  profession_category: z.string().min(1, 'اختيار الفرع إجباري'),
  food_description: z.string().max(1000).optional(),
  pickup_address: z.string().min(15, 'اكتب عنوان الشغل بالتفصيل').max(500),
  work_start_time: z.string().min(1, 'حدد ساعة بداية العمل'),
  work_end_time: z.string().min(1, 'حدد ساعة نهاية العمل'),
})).refine((value) => value.work_start_time !== value.work_end_time, {
  path: ['work_end_time'],
  message: 'ساعة نهاية العمل لازم تختلف عن ساعة البداية',
})

const forgotSchema = z.object({ email: z.email('أدخل بريدًا إلكترونيًا صحيحًا') })
const resetSchema = z.object({
  password: z.string().min(8, 'كلمة المرور لا تقل عن 8 أحرف'),
  password_confirm: z.string(),
}).refine((value) => value.password === value.password_confirm, {
  path: ['password_confirm'],
  message: 'كلمتا المرور غير متطابقتين',
})

type LoginValues = z.infer<typeof loginSchema>
type RegisterValues = z.infer<typeof registerSchema>
type WorkerRegisterValues = z.infer<typeof workerRegisterSchema>
type ForgotValues = z.infer<typeof forgotSchema>
type ResetValues = z.infer<typeof resetSchema>

const inputClass = 'field-control'

function FieldError({ message }: { message?: string }) {
  return message ? <p className="mt-1 text-xs text-rose-600">{message}</p> : null
}

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

function LoginForm({ onForgot }: { onForgot: () => void }) {
  const navigate = useNavigate()
  const location = useLocation()
  const setSession = useAuthStore((state) => state.setSession)
  const [serverError, setServerError] = useState('')
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginValues>({ resolver: zodResolver(loginSchema) })

  const submit = handleSubmit(async (values) => {
    setServerError('')
    try {
      const response = await auth.login(values)
      const session = response.data as Session
      setSession(session)
      const requestedPath = (location.state as { from?: string } | null)?.from
      navigate(requestedPath || (session.user.role === 'seller' ? '/seller' : '/'), { replace: true })
    } catch (error) {
      setServerError(errorMessage(error, 'تعذر تسجيل الدخول'))
    }
  })

  return (
    <form onSubmit={submit} className="space-y-3">
      <div>
        <input {...register('username')} autoComplete="username" placeholder="اسم المستخدم" className={inputClass} />
        <FieldError message={errors.username?.message} />
      </div>
      <div>
        <input {...register('password')} type="password" autoComplete="current-password" placeholder="كلمة المرور" className={inputClass} />
        <FieldError message={errors.password?.message} />
      </div>
      <button type="button" onClick={onForgot} className="text-sm font-bold text-brand-700">نسيت كلمة المرور؟</button>
      {serverError && <p className="rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{serverError}</p>}
      <button disabled={isSubmitting} className="primary-button w-full">{isSubmitting ? 'جاري الدخول...' : 'تسجيل الدخول'}</button>
    </form>
  )
}

function RegisterForm() {
  const [message, setMessage] = useState('')
  const [serverError, setServerError] = useState('')
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<RegisterValues>({ resolver: zodResolver(registerSchema) })
  const submit = handleSubmit(async (values) => {
    setServerError('')
    try {
      const response = await auth.register(values)
      setMessage(response.data.message)
    } catch (error) {
      setServerError(errorMessage(error, 'تعذر إنشاء الحساب'))
    }
  })

  if (message) return <div className="rounded-2xl bg-green-50 p-5 text-center text-green-800"><h2 className="font-black">راجع بريدك الإلكتروني</h2><p className="mt-2 text-sm">{message}</p></div>
  return (
    <form onSubmit={submit} className="grid gap-3">
      <div className="grid grid-cols-2 gap-2">
        <div><input {...register('first_name')} placeholder="الاسم الأول" className={inputClass} /><FieldError message={errors.first_name?.message} /></div>
        <div><input {...register('last_name')} placeholder="اسم العائلة" className={inputClass} /><FieldError message={errors.last_name?.message} /></div>
      </div>
      <div><input {...register('username')} autoComplete="username" placeholder="اسم المستخدم" className={inputClass} /><FieldError message={errors.username?.message} /></div>
      <div><input {...register('email')} type="email" autoComplete="email" placeholder="البريد الإلكتروني" className={inputClass} /><FieldError message={errors.email?.message} /></div>
      <div><input {...register('password')} type="password" autoComplete="new-password" placeholder="كلمة المرور" className={inputClass} /><FieldError message={errors.password?.message} /></div>
      <div><input {...register('password_confirm')} type="password" autoComplete="new-password" placeholder="تأكيد كلمة المرور" className={inputClass} /><FieldError message={errors.password_confirm?.message} /></div>
      {serverError && <p className="rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{serverError}</p>}
      <button disabled={isSubmitting} className="primary-button w-full">{isSubmitting ? 'جاري إنشاء الحساب...' : 'إنشاء حساب زبون'}</button>
    </form>
  )
}

function WorkerRegisterForm() {
  const locationsQuery = useLocations()
  const fallbackLocations = useMemo(() => localLocations(), [])
  const locations = locationsQuery.data?.length ? locationsQuery.data : fallbackLocations
  const [message, setMessage] = useState('')
  const [serverError, setServerError] = useState('')
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<WorkerRegisterValues>({
    resolver: zodResolver(workerRegisterSchema),
    defaultValues: {
      governorate: '',
      center: '',
      age: '',
      food_description: '',
      pickup_address: '',
      work_start_time: '09:00',
      work_end_time: '17:00',
      profession_trade: '',
      profession_category: '',
    },
  })
  const selectedGovernorate = watch('governorate')
  const selectedTradeId = watch('profession_trade')
  const centers = locations.find((item) => item.name_ar === selectedGovernorate)?.centers || []
  const selectedTrade = useMemo(() => trades.find((item) => item.id === selectedTradeId), [selectedTradeId])

  const submit = handleSubmit(async (values) => {
    setServerError('')
    try {
      const {
        profession_trade,
        profession_category,
        ...payload
      } = values
      const response = await auth.registerChef({
        ...payload,
        professions: [{ trade: profession_trade, category: profession_category }],
        age: Number(values.age),
      })
      setMessage(response.data.message)
    } catch (error) {
      setServerError(errorMessage(error, 'تعذر إنشاء حساب العامل'))
    }
  })

  if (message) {
    return (
      <div className="rounded-2xl bg-green-50 p-5 text-center text-green-800">
        <h2 className="font-black">تم إنشاء حساب العامل</h2>
        <p className="mt-2 text-sm">{message}</p>
      </div>
    )
  }

  return (
    <form onSubmit={submit} className="grid gap-3">
      <div className="grid grid-cols-2 gap-2">
        <div><input {...register('first_name')} placeholder="الاسم الأول" className={inputClass} /><FieldError message={errors.first_name?.message} /></div>
        <div><input {...register('last_name')} placeholder="اسم العائلة" className={inputClass} /><FieldError message={errors.last_name?.message} /></div>
      </div>
      <div><input {...register('kitchen_name')} placeholder="اسم العامل أو الورشة" className={inputClass} /><FieldError message={errors.kitchen_name?.message} /></div>
      <div className="grid grid-cols-2 gap-2">
        <div><input {...register('age')} type="number" min="18" max="80" placeholder="السن" className={inputClass} /><FieldError message={errors.age?.message} /></div>
        <div><input {...register('national_id')} inputMode="numeric" maxLength={14} placeholder="الرقم القومي" className={inputClass} /><FieldError message={errors.national_id?.message} /></div>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <select
            {...register('governorate')}
            className={inputClass}
            onChange={(event) => {
              register('governorate').onChange(event)
              setValue('center', '')
            }}
          >
            <option value="">المحافظة</option>
            {locations.map((item) => <option key={item.id} value={item.name_ar}>{item.name_ar}</option>)}
          </select>
          <FieldError message={errors.governorate?.message} />
        </div>
        <div>
          <select {...register('center')} className={inputClass} disabled={!selectedGovernorate}>
            <option value="">المركز</option>
            {centers.map((item) => <option key={item.id} value={item.name_ar}>{item.name_ar}</option>)}
          </select>
          <FieldError message={errors.center?.message} />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <select
            {...register('profession_trade')}
            className={inputClass}
            onChange={(event) => {
              register('profession_trade').onChange(event)
              setValue('profession_category', '')
            }}
          >
            <option value="">المهنة الأساسية</option>
            {trades.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
          </select>
          <FieldError message={errors.profession_trade?.message} />
        </div>
        <div>
          <select {...register('profession_category')} className={inputClass} disabled={!selectedTrade}>
            <option value="">الفرع الثانوي</option>
            {(selectedTrade?.categories || []).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
          </select>
          <FieldError message={errors.profession_category?.message} />
        </div>
      </div>
      <textarea {...register('food_description')} rows={3} placeholder="اكتب نبذة قصيرة عن شغلك وخبرتك" className={inputClass} />
      <div>
        <textarea {...register('pickup_address')} rows={2} placeholder="عنوان شغلك بالتفصيل: الشارع، العلامة المميزة، ونطاق الخدمة" className={inputClass} />
        <FieldError message={errors.pickup_address?.message} />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <label className="text-xs font-bold text-stone-600">
          يبدأ العمل
          <ArabicTimeSelect
            required
            value={watch('work_start_time')}
            onChange={(value) => setValue('work_start_time', value, { shouldValidate: true })}
            className={`${inputClass} mt-1`}
          />
          <FieldError message={errors.work_start_time?.message} />
        </label>
        <label className="text-xs font-bold text-stone-600">
          ينتهي العمل
          <ArabicTimeSelect
            required
            value={watch('work_end_time')}
            onChange={(value) => setValue('work_end_time', value, { shouldValidate: true })}
            className={`${inputClass} mt-1`}
          />
          <FieldError message={errors.work_end_time?.message} />
        </label>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div><input {...register('username')} autoComplete="username" placeholder="اسم المستخدم" className={inputClass} /><FieldError message={errors.username?.message} /></div>
        <div><input {...register('email')} type="email" autoComplete="email" placeholder="البريد الإلكتروني" className={inputClass} /><FieldError message={errors.email?.message} /></div>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div><input {...register('password')} type="password" autoComplete="new-password" placeholder="كلمة المرور" className={inputClass} /><FieldError message={errors.password?.message} /></div>
        <div><input {...register('password_confirm')} type="password" autoComplete="new-password" placeholder="تأكيد كلمة المرور" className={inputClass} /><FieldError message={errors.password_confirm?.message} /></div>
      </div>
      <p className="rounded-xl bg-amber-50 p-3 text-xs leading-5 text-amber-800">
        يتم استخدام الرقم القومي لمنع تكرار حساب العامل فقط، ويتم حفظ بصمة رقمية آمنة وآخر 4 أرقام.
      </p>
      {serverError && <p className="rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{serverError}</p>}
      <button disabled={isSubmitting || locationsQuery.isLoading} className="primary-button w-full">
        {isSubmitting ? 'جاري إنشاء حساب العامل...' : 'إنشاء حساب عامل'}
      </button>
    </form>
  )
}

function ForgotPassword({ onBack }: { onBack: () => void }) {
  const [message, setMessage] = useState('')
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<ForgotValues>({ resolver: zodResolver(forgotSchema) })
  const submit = handleSubmit(async (values) => {
    const response = await auth.forgotPassword(values)
    setMessage(response.data.message)
  })
  return (
    <form onSubmit={submit} className="space-y-3">
      <p className="text-sm leading-6 text-stone-600">أدخل بريدك وسنرسل رابطًا آمنًا لإعادة تعيين كلمة المرور.</p>
      <div><input {...register('email')} type="email" placeholder="البريد الإلكتروني" className={inputClass} /><FieldError message={errors.email?.message} /></div>
      {message && <p className="rounded-xl bg-green-50 p-3 text-sm text-green-700">{message}</p>}
      <button disabled={isSubmitting} className="w-full rounded-xl bg-stone-950 py-3 font-black text-white">إرسال الرابط</button>
      <button type="button" onClick={onBack} className="w-full text-sm font-bold text-brand-700">العودة للدخول</button>
    </form>
  )
}

function VerifyEmail() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const setSession = useAuthStore((state) => state.setSession)
  const [status, setStatus] = useState('جاري تأكيد البريد...')
  useEffect(() => {
    const uid = params.get('uid')
    const token = params.get('token')
    if (!uid || !token) return setStatus('رابط التحقق غير مكتمل')
    auth.verifyEmail({ uid, token })
      .then((response) => {
        setSession(dataOf<Session>(response))
        setStatus('تم تأكيد بريدك بنجاح')
        const session = dataOf<Session>(response)
        window.setTimeout(() => navigate(session.user.role === 'seller' ? '/seller' : '/', { replace: true }), 900)
      })
      .catch((error) => setStatus(errorMessage(error, 'تعذر تأكيد البريد')))
  }, [navigate, params, setSession])
  return <div className="rounded-2xl bg-white p-6 text-center font-bold soft-shadow">{status}</div>
}

function ResetPassword() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const [serverError, setServerError] = useState('')
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<ResetValues>({ resolver: zodResolver(resetSchema) })
  const submit = handleSubmit(async (values) => {
    try {
      await auth.resetPassword({ ...values, uid: params.get('uid'), token: params.get('token') })
      navigate('/auth', { replace: true })
    } catch (error) {
      setServerError(errorMessage(error, 'تعذر تغيير كلمة المرور'))
    }
  })
  return (
    <form onSubmit={submit} className="space-y-3">
      <div><input {...register('password')} type="password" placeholder="كلمة المرور الجديدة" className={inputClass} /><FieldError message={errors.password?.message} /></div>
      <div><input {...register('password_confirm')} type="password" placeholder="تأكيد كلمة المرور" className={inputClass} /><FieldError message={errors.password_confirm?.message} /></div>
      {serverError && <p className="rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{serverError}</p>}
      <button disabled={isSubmitting} className="w-full rounded-xl bg-stone-950 py-3 font-black text-white">تغيير كلمة المرور</button>
    </form>
  )
}

export default function Auth() {
  const { pathname } = useLocation()
  const [mode, setMode] = useState<'login' | 'register' | 'worker' | 'forgot'>('login')
  const special = pathname.endsWith('/verify') ? <VerifyEmail /> : pathname.endsWith('/reset-password') ? <ResetPassword /> : null
  return (
    <main className="relative grid min-h-[calc(100vh-116px)] place-items-center overflow-hidden px-4 py-10 pb-28">
      <section className={`surface-card auth-card relative w-full p-6 sm:p-8 ${mode === 'worker' ? 'max-w-2xl' : 'max-w-md'}`}>
        <div className="mb-7 text-center">
          <span className="mx-auto grid h-16 w-16 place-items-center overflow-hidden rounded-2xl bg-[#e6f2bd] shadow-lg">
            <img src="/brand/sanati-mark.png" alt="" className="h-full w-full object-contain" />
          </span>
          <h1 className="mt-4 text-2xl font-extrabold tracking-tight text-forest-900">صنعتى</h1>
          <p className="mt-2 text-sm leading-6 text-stone-500">دخول واضح للزبون والعامل، وكل عامل يحدد مهنته وفرعه وعنوان شغله.</p>
        </div>
        {special || (
          <>
            {mode !== 'forgot' && (
              <div className="mb-6 grid grid-cols-3 rounded-xl bg-[#f3f1ec] p-1">
                <button onClick={() => setMode('login')} className={`rounded-lg py-2.5 text-xs font-bold transition sm:text-sm ${mode === 'login' ? 'bg-white text-forest-900 shadow-sm' : 'text-stone-500'}`}>دخول</button>
                <button onClick={() => setMode('register')} className={`rounded-lg py-2.5 text-xs font-bold transition sm:text-sm ${mode === 'register' ? 'bg-white text-forest-900 shadow-sm' : 'text-stone-500'}`}>حساب زبون</button>
                <button onClick={() => setMode('worker')} className={`rounded-lg py-2.5 text-xs font-bold transition sm:text-sm ${mode === 'worker' ? 'bg-white text-forest-900 shadow-sm' : 'text-stone-500'}`}>حساب عامل</button>
              </div>
            )}
            {mode === 'login'
              ? <LoginForm onForgot={() => setMode('forgot')} />
              : mode === 'register'
                ? <RegisterForm />
                : mode === 'worker'
                  ? <WorkerRegisterForm />
                  : <ForgotPassword onBack={() => setMode('login')} />}
          </>
        )}
      </section>
    </main>
  )
}
