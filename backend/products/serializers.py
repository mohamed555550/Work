from rest_framework import serializers
from django.utils import timezone
from .models import Product
from sellers.serializers import SellerPublicSerializer


class ProductSerializer(serializers.ModelSerializer):
    seller = SellerPublicSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    can_order = serializers.BooleanField(read_only=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'ingredients', 'price', 'image', 'images',
            'category', 'listing_type', 'trade', 'trade_category',
            'preparation_time', 'is_available', 'available_at',
            'can_order', 'seller', 'average_rating', 'review_count',
        ]

    def get_average_rating(self, obj) -> float:
        annotated = getattr(obj, 'rating_value', None)
        return round(float(annotated), 1) if annotated is not None else obj.average_rating

    def get_review_count(self, obj) -> int:
        annotated = getattr(obj, 'rating_count', None)
        return int(annotated) if annotated is not None else obj.review_count

    def get_images(self, obj) -> list[str]:
        urls = []
        if obj.image:
            urls.append(obj.image.url)
        for item in obj.images.all():
            if item.image:
                urls.append(item.image.url)
        seen = set()
        return [url for url in urls if not (url in seen or seen.add(url))]


class ProductCreateSerializer(serializers.ModelSerializer):
    ingredients = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'ingredients', 'price', 'image',
            'category', 'listing_type', 'trade', 'trade_category',
            'preparation_time', 'is_available', 'available_at',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        is_available = attrs.get(
            'is_available',
            self.instance.is_available if self.instance else True,
        )
        available_at = attrs.get(
            'available_at',
            self.instance.available_at if self.instance else None,
        )
        if is_available:
            attrs['available_at'] = None
        elif not available_at:
            raise serializers.ValidationError({
                'available_at': 'ط­ط¯ط¯ ظ…ظˆط¹ط¯ ط¥طھط§ط­ط© ط§ظ„ظˆط¬ط¨ط© ظ„ظ„ط¹ظ…ظ„ط§ط،',
            })
        elif available_at <= timezone.now():
            raise serializers.ValidationError({
                'available_at': 'ظ…ظˆط¹ط¯ ط§ظ„ط¥طھط§ط­ط© ظٹط¬ط¨ ط£ظ† ظٹظƒظˆظ† ظپظٹ ط§ظ„ظ…ط³طھظ‚ط¨ظ„',
            })
        return attrs

    def validate_ingredients(self, value):
        value = value.strip()
        if value and len(value) < 3:
            raise serializers.ValidationError('اكتب وصفا أوضح')
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError('السعر لا يمكن أن يكون أقل من صفر')
        return value

    def validate_preparation_time(self, value):
        if value < 5:
            raise serializers.ValidationError('وقت التجهيز يجب ألا يقل عن 5 دقائق')
        return value

    def validate_image(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('ط­ط¬ظ… ط§ظ„طµظˆط±ط© ظٹط¬ط¨ ط£ظ„ط§ ظٹطھط¬ط§ظˆط² 5 ظ…ظٹط¬ط§ط¨ط§ظٹطھ')
        if value and getattr(value, 'content_type', '') not in {'image/jpeg', 'image/png', 'image/webp'}:
            raise serializers.ValidationError('طµظٹط؛ط© ط§ظ„طµظˆط±ط© ظٹط¬ط¨ ط£ظ† طھظƒظˆظ† JPG ط£ظˆ PNG ط£ظˆ WebP')
        return value

    def create(self, validated_data):
        seller = self.context['request'].user.seller_profile
        return Product.objects.create(seller=seller, **validated_data)


class RecommendedProductSerializer(ProductSerializer):
    recommendation_score = serializers.FloatField(source='ai_score', read_only=True)
    recommendation_reason = serializers.CharField(read_only=True)

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + [
            'recommendation_score',
            'recommendation_reason',
        ]


class RecommendedChefSerializer(SellerPublicSerializer):
    recommendation_score = serializers.FloatField(source='ai_score', read_only=True)
    recommendation_reason = serializers.CharField(read_only=True)

    class Meta(SellerPublicSerializer.Meta):
        fields = SellerPublicSerializer.Meta.fields + [
            'recommendation_score',
            'recommendation_reason',
        ]


class SearchInterpretationSerializer(serializers.Serializer):
    cheap = serializers.BooleanField()
    best = serializers.BooleanField()
    category = serializers.CharField(allow_blank=True)
    governorate = serializers.CharField(allow_blank=True)
    center = serializers.CharField(allow_blank=True)


class AISearchResultSerializer(serializers.Serializer):
    normalized_query = serializers.CharField()
    interpretation = SearchInterpretationSerializer()
    meals = RecommendedProductSerializer(many=True)
    chefs = RecommendedChefSerializer(many=True)


class RecommendationResultSerializer(serializers.Serializer):
    meals = RecommendedProductSerializer(many=True)
    chefs = RecommendedChefSerializer(many=True)

