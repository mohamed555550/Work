from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.db.models import Avg, Count
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.core.cache import cache
from hashlib import sha256
from rest_framework import filters, generics, permissions
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import OpenApiParameter, extend_schema
from .models import MealImage, Product, SearchHistory
from .serializers import (
    ProductSerializer,
    ProductCreateSerializer,
    RecommendedChefSerializer,
    RecommendedProductSerializer,
    AISearchResultSerializer,
    RecommendationResultSerializer,
)
from .recommendations import recommendation_version, recommendations_for, semantic_search
from common.utils import success_response, error_response


MAX_GALLERY_IMAGES = 30
MAX_GALLERY_IMAGE_SIZE = 10 * 1024 * 1024
ALLOWED_GALLERY_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}


def _validate_gallery_upload(upload):
    if upload.size > MAX_GALLERY_IMAGE_SIZE:
        raise ValidationError({'images': 'حجم كل صورة يجب ألا يتجاوز 10 ميجابايت'})
    if getattr(upload, 'content_type', '') not in ALLOWED_GALLERY_IMAGE_TYPES:
        raise ValidationError({'images': 'صيغة الصور يجب أن تكون JPG أو PNG أو WebP أو GIF'})


def _attach_product_images(product, files):
    if not files:
        return
    if len(files) > MAX_GALLERY_IMAGES:
        raise ValidationError({'images': f'يمكن رفع حتى {MAX_GALLERY_IMAGES} صورة في المرة الواحدة'})
    for upload in files:
        _validate_gallery_upload(upload)

    gallery_files = list(files)
    if not product.image and gallery_files:
        product.image = gallery_files.pop(0)
        product.save(update_fields=['image'])

    current_count = product.images.count()
    for index, upload in enumerate(gallery_files, start=current_count):
        MealImage.objects.create(meal=product, image=upload, sort_order=index)


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'seller__name']

    def get_queryset(self):
        return (
            Product.objects
            .filter(seller__approved='approved')
            .filter(Q(is_available=True) | Q(available_at__isnull=False))
            .select_related('seller__user')
            .prefetch_related('images', 'reviews')
            .annotate(rating_value=Avg('reviews__rating'), rating_count=Count('reviews'))
            .order_by('-created_at', '-id')
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        governorate = request.query_params.get('governorate')
        center = request.query_params.get('center')
        category = request.query_params.get('category')
        listing_type = request.query_params.get('listing_type')
        trade = request.query_params.get('trade')
        trade_category = request.query_params.get('trade_category')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        rating = request.query_params.get('rating')
        seller = request.query_params.get('seller')

        if governorate:
            queryset = queryset.filter(seller__governorate__iexact=governorate)
        if center:
            queryset = queryset.filter(seller__center__iexact=center)
        if category:
            queryset = queryset.filter(category=category)
        if listing_type:
            queryset = queryset.filter(listing_type=listing_type)
        if trade:
            queryset = queryset.filter(Q(trade=trade) | Q(trade='all'))
        if trade_category:
            queryset = queryset.filter(Q(trade_category=trade_category) | Q(trade='all') | Q(trade_category='all'))
        if seller:
            if not seller.isdigit():
                raise ValidationError('معرّف العامل غير صحيح')
            queryset = queryset.filter(seller_id=int(seller))
        try:
            if min_price:
                queryset = queryset.filter(price__gte=Decimal(min_price))
            if max_price:
                queryset = queryset.filter(price__lte=Decimal(max_price))
            if rating:
                rating_value = Decimal(rating)
                if not 0 <= rating_value <= 5:
                    raise InvalidOperation
                queryset = queryset.filter(rating_value__gte=rating_value)
        except (InvalidOperation, ValueError):
            raise ValidationError('قيم السعر أو التقييم غير صحيحة')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data = {
                'success': True,
                'data': response.data['results'],
                'pagination': {
                    'count': response.data['count'],
                    'next': response.data['next'],
                    'previous': response.data['previous'],
                },
                'message': '',
            }
            return response
        return success_response(data=self.get_serializer(queryset, many=True).data)


class SellerProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not hasattr(self.request.user, 'seller_profile'):
            return Product.objects.none()
        return Product.objects.filter(seller=self.request.user.seller_profile).select_related('seller__user').prefetch_related('images')

    def list(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_queryset(), many=True).data)


class AdminProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Product.objects.select_related('seller__user').prefetch_related('images', 'reviews').order_by('-created_at')

    def list(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_queryset(), many=True).data)


class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not hasattr(request.user, 'seller_profile') or not request.user.seller_profile.is_active_seller:
            return error_response('يجب أن تكون عاملاً معتمداً لإضافة المنتجات', status=403)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            product = serializer.save()
            _attach_product_images(
                product,
                list(request.FILES.getlist('images')) + list(request.FILES.getlist('images[]')),
            )
        data = ProductSerializer(product, context=self.get_serializer_context()).data
        return success_response(data=data, message='تم إنشاء المعروض بنجاح')


class ProductManageView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Product.objects.all().prefetch_related('images')
        if hasattr(self.request.user, 'seller_profile'):
            return Product.objects.filter(seller=self.request.user.seller_profile).prefetch_related('images')
        return Product.objects.none()

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            super().update(request, *args, **kwargs)
            product = self.get_object()
            _attach_product_images(
                product,
                list(request.FILES.getlist('images')) + list(request.FILES.getlist('images[]')),
            )
        data = ProductSerializer(product, context=self.get_serializer_context()).data
        return success_response(data=data, message='تم تحديث المعروض')

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        try:
            product.delete()
            message = 'تم حذف المنتج'
        except ProtectedError:
            product.is_available = False
            product.save(update_fields=['is_available'])
            message = 'تمت أرشفة المنتج لارتباطه بطلبات سابقة'
        return success_response(message=message)


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return (
            Product.objects
            .filter(seller__approved='approved')
            .filter(Q(is_available=True) | Q(available_at__isnull=False))
            .select_related('seller__user')
            .prefetch_related('images', 'reviews')
        )

    def retrieve(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_object()).data)


class AIRecommendationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RecommendationResultSerializer

    @extend_schema(parameters=[
        OpenApiParameter('governorate', str, description='اسم المحافظة'),
        OpenApiParameter('center', str, description='اسم المركز'),
    ])
    def get(self, request):
        governorate = request.query_params.get('governorate', '').strip()[:120]
        center = request.query_params.get('center', '').strip()[:120]
        version = recommendation_version(request.user.id)
        cache_key = f"recommendations:v1:{request.user.id}:{version}:{sha256(f'{governorate}|{center}'.encode()).hexdigest()[:16]}"
        cached = cache.get(cache_key)
        if cached is not None:
            return success_response(data=cached)

        result = recommendations_for(request.user, governorate, center)
        favorite_chef_ids = set(
            request.user.favorites.filter(chef__isnull=False).values_list('chef_id', flat=True)
        )
        followed_chef_ids = set(
            request.user.chef_follows.values_list('chef_id', flat=True)
        )
        for chef in result['chefs']:
            chef.is_favorite_value = chef.id in favorite_chef_ids
            chef.is_following_value = chef.id in followed_chef_ids
        payload = {
            'meals': RecommendedProductSerializer(
                result['meals'], many=True, context={'request': request}
            ).data,
            'chefs': RecommendedChefSerializer(
                result['chefs'], many=True, context={'request': request}
            ).data,
        }
        cache.set(cache_key, payload, timeout=300)
        return success_response(data=payload)


class AISearchView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AISearchResultSerializer

    @extend_schema(parameters=[
        OpenApiParameter('q', str, required=True, description='عبارة بحث طبيعية'),
        OpenApiParameter('governorate', str, description='المحافظة الافتراضية'),
        OpenApiParameter('center', str, description='المركز الافتراضي'),
    ])
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if len(query) < 2:
            raise ValidationError({'q': 'اكتب كلمتين على الأقل للبحث'})
        if len(query) > 500:
            raise ValidationError({'q': 'عبارة البحث طويلة جدًا'})
        governorate = request.query_params.get('governorate', '').strip()[:120]
        center = request.query_params.get('center', '').strip()[:120]
        normalized_key = sha256(
            f'{query.lower()}|{governorate}|{center}'.encode()
        ).hexdigest()
        audience = (
            f'{request.user.id}:{recommendation_version(request.user.id)}'
            if request.user.is_authenticated
            else 'anon'
        )
        cache_key = f'ai-search:v1:{audience}:{normalized_key}'
        result = cache.get(cache_key)
        if result is None:
            engine_result = semantic_search(query, governorate, center)
            if request.user.is_authenticated:
                favorite_chef_ids = set(
                    request.user.favorites.filter(chef__isnull=False)
                    .values_list('chef_id', flat=True)
                )
                followed_chef_ids = set(
                    request.user.chef_follows.values_list('chef_id', flat=True)
                )
                for chef in engine_result['chefs']:
                    chef.is_favorite_value = chef.id in favorite_chef_ids
                    chef.is_following_value = chef.id in followed_chef_ids
            result = {
                'normalized_query': engine_result['normalized_query'],
                'interpretation': engine_result['interpretation'],
                'meals': RecommendedProductSerializer(
                    engine_result['meals'], many=True, context={'request': request}
                ).data,
                'chefs': RecommendedChefSerializer(
                    engine_result['chefs'], many=True, context={'request': request}
                ).data,
            }
            cache.set(cache_key, result, timeout=120)
        if request.user.is_authenticated:
            SearchHistory.objects.create(
                user=request.user,
                query=query,
                normalized_query=result['normalized_query'],
                governorate=result['interpretation'].get('governorate', governorate),
                center=result['interpretation'].get('center', center),
            )
        return success_response(data=result)
