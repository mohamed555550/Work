from rest_framework import generics, permissions
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
import logging
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from .models import User
from .serializers import (
    EmailVerificationSerializer,
    ChefRegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserSerializer,
    SuggestionSerializer,
)
from .emails import _token_url, send_password_reset_email, send_verification_email
from .tokens import email_verification_token
from common.throttles import AuthRateThrottle
from common.utils import error_response, success_response

logger = logging.getLogger(__name__)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    throttle_classes = [AuthRateThrottle]


class RefreshView(TokenRefreshView):
    throttle_classes = [AuthRateThrottle]


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data['refresh']).blacklist()
        except Exception:
            return error_response('رمز الجلسة غير صالح', status=400)
        return success_response(message='تم تسجيل الخروج')


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthRateThrottle]
    success_message = 'تم إنشاء الحساب. تحقق من بريدك الإلكتروني لتفعيله'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if settings.EMAIL_VERIFICATION_REQUIRED:
            try:
                send_verification_email(user)
            except Exception:
                logger.exception('Unable to send verification email for user %s', user.pk)
        refresh = RefreshToken.for_user(user)
        return success_response(
            data={
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user, context={'request': request}).data,
            },
            message=self.success_message,
        )


class ChefRegisterView(RegisterView):
    serializer_class = ChefRegisterSerializer
    success_message = 'تم إنشاء حساب العامل وتفعيله. أكّد بريدك الإلكتروني لبدء نشر خدماتك ومنتجاتك.'


class EmailVerificationView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = _user_from_uid(serializer.validated_data['uid'])
        if not user or not email_verification_token.check_token(user, serializer.validated_data['token']):
            return error_response('رابط التحقق غير صالح أو منتهي', status=400)
        if not user.email_verified:
            user.email_verified = True
            user.save(update_fields=['email_verified'])
        refresh = RefreshToken.for_user(user)
        return success_response(data={
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user, context={'request': request}).data,
        }, message='تم تأكيد البريد الإلكتروني')


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(
            email__iexact=serializer.validated_data['email'],
            is_active=True,
        ).first()
        reset_url = None
        if user:
            try:
                send_password_reset_email(user)
            except Exception:
                logger.exception('Unable to send password reset email for user %s', user.pk)
            if settings.EMAIL_BACKEND.endswith('console.EmailBackend') or not settings.EMAIL_HOST_USER:
                reset_url = _token_url('/auth/reset-password', user)
        return success_response(
            data={'reset_url': reset_url} if reset_url else {},
            message='إذا كان البريد مسجلاً فستصلك رسالة إعادة التعيين',
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = _user_from_uid(serializer.validated_data['uid'])
        if not user or not default_token_generator.check_token(user, serializer.validated_data['token']):
            return error_response('رابط إعادة التعيين غير صالح أو منتهي', status=400)
        user.set_password(serializer.validated_data['password'])
        user.save(update_fields=['password'])
        for outstanding in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=outstanding)
        return success_response(message='تم تغيير كلمة المرور بنجاح')


def _user_from_uid(uid):
    try:
        return User.objects.get(pk=force_str(urlsafe_base64_decode(uid)))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_object()).data)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        super().update(request, *args, **kwargs)
        return success_response(data=self.get_serializer(self.get_object()).data, message='تم تحديث الملف الشخصي')


class SuggestionCreateView(generics.CreateAPIView):
    serializer_class = SuggestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.user.role not in {'user', 'seller'}:
            return error_response('الاقتراحات متاحة للزبائن والعمال', status=403)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        suggestion = serializer.save(user=request.user)
        delivered = False
        try:
            send_mail(
                subject=f'[Sanati Suggestion] {suggestion.subject}',
                message=(
                    f'From: {request.user.get_full_name() or request.user.username}\n'
                    f'Email: {request.user.email}\n'
                    f'Role: {request.user.role}\n'
                    f'User ID: {request.user.id}\n\n'
                    f'{suggestion.message}'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.SUGGESTIONS_EMAIL],
                fail_silently=False,
            )
            suggestion.status = 'sent'
            suggestion.email_sent_at = timezone.now()
            delivered = True
        except Exception as exc:
            logger.exception('Unable to email suggestion %s', suggestion.id)
            suggestion.status = 'failed'
            suggestion.email_error = str(exc)[:500]
        suggestion.save(update_fields=['status', 'email_sent_at', 'email_error'])
        data = SuggestionSerializer(suggestion, context={'request': request}).data
        data['delivered'] = delivered
        return success_response(
            data=data,
            message='تم إرسال اقتراحك، شكرًا لمساعدتنا في التحسين',
            status=201,
        )
