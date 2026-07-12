import hashlib
import hmac

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Suggestion, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'profile_image', 'is_staff', 'is_active', 'email_verified']
        read_only_fields = ['role', 'is_staff', 'is_active', 'email_verified']

    def validate_email(self, value):
        if value and User.objects.exclude(pk=getattr(self.instance, 'pk', None)).filter(email__iexact=value).exists():
            raise serializers.ValidationError('البريد الإلكتروني مستخدم بالفعل')
        return value.lower()


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if settings.EMAIL_VERIFICATION_REQUIRED and not self.user.email_verified:
            raise serializers.ValidationError({'email': 'يجب تأكيد البريد الإلكتروني قبل تسجيل الدخول'})
        data['user'] = UserSerializer(self.user, context=self.context).data
        return data


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'كلمة المرور غير متطابقة'})
        validate_password(attrs['password'])
        return attrs

    def validate_email(self, value):
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('البريد الإلكتروني مستخدم بالفعل')
        return value.lower()

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email_verified=not settings.EMAIL_VERIFICATION_REQUIRED,
        )


class ChefRegisterSerializer(RegisterSerializer):
    kitchen_name = serializers.CharField(max_length=180)
    governorate = serializers.CharField(max_length=120)
    center = serializers.CharField(max_length=120)
    age = serializers.IntegerField(min_value=18, max_value=80)
    national_id = serializers.RegexField(
        regex=r'^\d{14}$',
        write_only=True,
        error_messages={'invalid': 'الرقم القومي يجب أن يتكون من 14 رقمًا'},
    )
    food_description = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    professions = serializers.ListField(child=serializers.DictField(), required=True, allow_empty=False)
    pickup_address = serializers.CharField(min_length=15, max_length=500)
    work_start_time = serializers.TimeField(required=True)
    work_end_time = serializers.TimeField(required=True)

    class Meta(RegisterSerializer.Meta):
        fields = RegisterSerializer.Meta.fields + [
            'kitchen_name',
            'governorate',
            'center',
            'age',
            'national_id',
            'food_description',
            'professions',
            'pickup_address',
            'work_start_time',
            'work_end_time',
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        from sellers.models import Center, SellerProfile

        center_record = (
            Center.objects
            .select_related('governorate')
            .filter(
                governorate__name_ar=attrs['governorate'],
                name_ar=attrs['center'],
                governorate__is_active=True,
                is_active=True,
            )
            .first()
        )
        if not center_record:
            raise serializers.ValidationError({'center': 'اختر مركزًا صحيحًا تابعًا للمحافظة'})

        professions = attrs.get('professions') or []
        if not any(item.get('trade') and item.get('category') for item in professions if isinstance(item, dict)):
            raise serializers.ValidationError({'professions': 'اختيار المهنة والفرع الثانوي إجباري'})

        national_id = attrs['national_id']
        national_id_hash = hmac.new(
            settings.SECRET_KEY.encode(),
            national_id.encode(),
            hashlib.sha256,
        ).hexdigest()
        if SellerProfile.objects.filter(national_id_hash=national_id_hash).exists():
            raise serializers.ValidationError({'national_id': 'الرقم القومي مسجل بالفعل'})

        if attrs.get('work_start_time') == attrs.get('work_end_time'):
            raise serializers.ValidationError({'work_end_time': 'ساعة نهاية العمل لازم تختلف عن ساعة البداية'})

        attrs['_center_record'] = center_record
        attrs['_national_id_hash'] = national_id_hash
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        from sellers.models import SellerProfile

        center_record = validated_data.pop('_center_record')
        national_id_hash = validated_data.pop('_national_id_hash')
        national_id = validated_data.pop('national_id')
        kitchen_name = validated_data.pop('kitchen_name')
        age = validated_data.pop('age')
        food_description = validated_data.pop('food_description', '')
        professions = validated_data.pop('professions')
        pickup_address = validated_data.pop('pickup_address')
        work_start_time = validated_data.pop('work_start_time')
        work_end_time = validated_data.pop('work_end_time')
        validated_data.pop('governorate')
        validated_data.pop('center')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='seller',
            email_verified=not settings.EMAIL_VERIFICATION_REQUIRED,
        )
        SellerProfile.objects.create(
            user=user,
            name=kitchen_name,
            governorate=center_record.governorate.name_ar,
            center=center_record.name_ar,
            governorate_record=center_record.governorate,
            center_record=center_record,
            food_description=food_description or 'خدمات ومنتجات حرفية حسب الطلب.',
            professions=professions,
            pickup_address=pickup_address,
            work_start_time=work_start_time,
            work_end_time=work_end_time,
            age=age,
            national_id_hash=national_id_hash,
            national_id_last4=national_id[-4:],
            approved='approved',
        )
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'كلمتا المرور غير متطابقتين'})
        validate_password(attrs['password'])
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class SuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suggestion
        fields = ['id', 'subject', 'message', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

    def validate_subject(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError('عنوان الاقتراح قصير جدًا')
        if '\r' in value or '\n' in value:
            raise serializers.ValidationError('عنوان الاقتراح غير صالح')
        return value

    def validate_message(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError('اكتب تفاصيل أكثر عن اقتراحك')
        return value
