import hashlib
import hmac

from django.conf import settings
from rest_framework import serializers
from .models import Center, Governorate, KitchenGallery, SellerProfile


class CenterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name_ar')
    name_ar = serializers.CharField(read_only=True)
    name_en = serializers.CharField(read_only=True)

    class Meta:
        model = Center
        fields = ['id', 'name', 'name_ar', 'name_en', 'slug']


class GovernorateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name_ar')
    name_ar = serializers.CharField(read_only=True)
    name_en = serializers.CharField(read_only=True)
    centers = CenterSerializer(many=True, read_only=True)

    class Meta:
        model = Governorate
        fields = [
            'id', 'icon', 'name', 'name_ar', 'name_en', 'slug',
            'estimated_population', 'population_as_of', 'centers',
        ]


class SellerActionResultSerializer(serializers.Serializer):
    following = serializers.BooleanField(required=False)
    favorite = serializers.BooleanField(required=False)


def validate_professions(value):
    if not any(item.get('trade') and item.get('category') for item in value if isinstance(item, dict)):
        raise serializers.ValidationError('اختيار المهنة والفرع الثانوي إجباري')
    return value


class SellerProfileSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='user.get_full_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    profile_image = serializers.ImageField(
        source='user.profile_image',
        required=False,
        allow_null=True,
    )
    work_gallery = serializers.SerializerMethodField()

    class Meta:
        model = SellerProfile
        fields = [
            'id', 'name', 'owner', 'username', 'email', 'governorate', 'center',
            'food_description', 'professions', 'pickup_address', 'cover_image', 'profile_image',
            'age', 'national_id_last4', 'experience_years', 'is_open',
            'work_start_time', 'work_end_time', 'approved',
            'work_gallery', 'created_at', 'updated_at',
        ]
        read_only_fields = ['national_id_last4', 'approved', 'created_at', 'updated_at']

    def _validate_image(self, value):
        if value and value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('حجم الصورة يجب ألا يتجاوز 10 ميجابايت')
        if value and getattr(value, 'content_type', '') not in {
            'image/jpeg', 'image/png', 'image/webp', 'image/gif',
        }:
            raise serializers.ValidationError('صيغة الصورة غير مدعومة')
        return value

    def validate(self, attrs):
        start = attrs.get('work_start_time', getattr(self.instance, 'work_start_time', None))
        end = attrs.get('work_end_time', getattr(self.instance, 'work_end_time', None))
        if not start or not end:
            raise serializers.ValidationError({
                'work_start_time': 'حدد ساعة بداية العمل',
                'work_end_time': 'حدد ساعة نهاية العمل',
            })
        if start == end:
            raise serializers.ValidationError({'work_end_time': 'ساعة نهاية العمل لازم تختلف عن ساعة البداية'})

        professions = attrs.get('professions')
        if professions is not None:
            validate_professions(professions)
        return attrs

    def validate_cover_image(self, value):
        return self._validate_image(value)

    def validate_profile_image(self, value):
        return self._validate_image(value)

    def validate_pickup_address(self, value):
        value = value.strip()
        if len(value) < 15:
            raise serializers.ValidationError('اكتب عنوان الشغل بالتفصيل')
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        profile_image = user_data.get('profile_image', serializers.empty)
        if profile_image is not serializers.empty:
            instance.user.profile_image = profile_image
            instance.user.save(update_fields=['profile_image'])
        return super().update(instance, validated_data)

    def get_work_gallery(self, obj):
        return WorkGallerySerializer(obj.kitchen_gallery.all(), many=True, context=self.context).data


class WorkGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = KitchenGallery
        fields = ['id', 'image', 'caption', 'sort_order', 'created_at']
        read_only_fields = ['id', 'sort_order', 'created_at']

    def validate_image(self, value):
        if value and value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('حجم الصورة يجب ألا يتجاوز 10 ميجابايت')
        if value and getattr(value, 'content_type', '') not in {
            'image/jpeg', 'image/png', 'image/webp', 'image/gif',
        }:
            raise serializers.ValidationError('صيغة الصورة غير مدعومة')
        return value

    def validate_caption(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError('اكتب وصفا أوضح للشغل')
        return value


class SellerPublicSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    order_count = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    cover_image = serializers.ImageField(read_only=True)
    profile_image = serializers.ImageField(source='user.profile_image', read_only=True)
    is_following = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    work_gallery = serializers.SerializerMethodField()

    class Meta:
        model = SellerProfile
        fields = [
            'id', 'name', 'governorate', 'center', 'food_description', 'approved',
            'professions', 'pickup_address', 'cover_image', 'profile_image', 'rating', 'reviews_count',
            'followers_count', 'order_count', 'product_count', 'experience_years',
            'is_open', 'work_start_time', 'work_end_time', 'is_online',
            'is_following', 'is_favorite', 'work_gallery',
        ]
        read_only_fields = fields

    def get_rating(self, obj) -> float:
        return round(float(getattr(obj, 'rating_value', 0) or 0), 1)

    def get_order_count(self, obj) -> int:
        return int(getattr(obj, 'order_count_value', 0) or 0)

    def get_product_count(self, obj) -> int:
        return int(getattr(obj, 'product_count_value', 0) or 0)

    def get_reviews_count(self, obj) -> int:
        return int(getattr(obj, 'reviews_count_value', 0) or 0)

    def get_followers_count(self, obj) -> int:
        return int(getattr(obj, 'followers_count_value', 0) or 0)

    def get_is_following(self, obj) -> bool:
        return bool(getattr(obj, 'is_following_value', False))

    def get_is_favorite(self, obj) -> bool:
        return bool(getattr(obj, 'is_favorite_value', False))

    def get_work_gallery(self, obj):
        return WorkGallerySerializer(obj.kitchen_gallery.all(), many=True, context=self.context).data


class SellerApplicationSerializer(serializers.ModelSerializer):
    national_id = serializers.RegexField(regex=r'^\d{14}$', write_only=True)
    age = serializers.IntegerField(min_value=18, max_value=80)
    pickup_address = serializers.CharField(min_length=15, max_length=500)
    work_start_time = serializers.TimeField(required=True)
    work_end_time = serializers.TimeField(required=True)

    class Meta:
        model = SellerProfile
        fields = [
            'id', 'name', 'governorate', 'center', 'food_description',
            'professions', 'pickup_address', 'age', 'national_id',
            'work_start_time', 'work_end_time',
        ]
        read_only_fields = ['id']

    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError('اسم العامل أو الورشة قصير جدًا')
        return value

    def validate(self, attrs):
        center_record = (
            Center.objects.select_related('governorate')
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
        if attrs.get('work_start_time') == attrs.get('work_end_time'):
            raise serializers.ValidationError({'work_end_time': 'ساعة نهاية العمل لازم تختلف عن ساعة البداية'})
        validate_professions(attrs.get('professions') or [])

        national_id_hash = hmac.new(
            settings.SECRET_KEY.encode(),
            attrs['national_id'].encode(),
            hashlib.sha256,
        ).hexdigest()
        if SellerProfile.objects.filter(national_id_hash=national_id_hash).exists():
            raise serializers.ValidationError({'national_id': 'الرقم القومي مسجل بالفعل'})
        attrs['_center_record'] = center_record
        attrs['_national_id_hash'] = national_id_hash
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        center_record = validated_data.pop('_center_record')
        national_id_hash = validated_data.pop('_national_id_hash')
        national_id = validated_data.pop('national_id')
        user.role = 'seller'
        user.save(update_fields=['role'])
        return SellerProfile.objects.create(
            user=user,
            approved='approved',
            governorate_record=center_record.governorate,
            center_record=center_record,
            national_id_hash=national_id_hash,
            national_id_last4=national_id[-4:],
            **validated_data,
        )
