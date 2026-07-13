from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import email_verification_token


def _token_url(path: str, user, generator=default_token_generator) -> str:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = generator.make_token(user)
    route = path if path.startswith('/') else f'/{path}'
    return f"{settings.FRONTEND_URL.rstrip('/')}/#{route}?uid={uid}&token={token}"


def send_verification_email(user) -> None:
    url = _token_url('/auth/verify', user, email_verification_token)
    send_mail(
        subject='تأكيد بريدك في صنعتى',
        message=f'مرحباً {user.first_name or user.username}،\n\nأكد بريدك من الرابط التالي:\n{url}\n\nينتهي الرابط تلقائياً لأسباب أمنية.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


def send_password_reset_email(user) -> None:
    url = _token_url('/auth/reset-password', user)
    send_mail(
        subject='إعادة تعيين كلمة المرور',
        message=f'طلبت إعادة تعيين كلمة المرور.\n\nاستخدم الرابط التالي:\n{url}\n\nإذا لم تطلب ذلك فتجاهل الرسالة.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
