from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.db import connection
from django.db.models import Avg, Count, Exists, OuterRef, Q
from rest_framework.filters import SearchFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from django.shortcuts import get_object_or_404
from .models import Follower, Governorate, SellerProfile
from .serializers import (
    GovernorateSerializer,
    SellerApplicationSerializer,
    SellerProfileSerializer,
    SellerPublicSerializer,
    SellerActionResultSerializer,
)
from common.utils import success_response, error_response
from audit_logs.models import AuditLog
from notifications.models import Notification
from favorites.models import Favorite


def public_seller_queryset(user=None):
    queryset = SellerProfile.objects.filter(approved='approved').select_related('user').annotate(
        rating_value=Avg('products__reviews__rating'),
        reviews_count_value=Count('products__reviews', distinct=True),
        followers_count_value=Count('followers', distinct=True),
        order_count_value=Count('orders', filter=Q(orders__status='completed'), distinct=True),
        product_count_value=Count('products', filter=Q(products__is_available=True), distinct=True),
    )
    if user and user.is_authenticated:
        queryset = queryset.annotate(
            is_following_value=Exists(
                Follower.objects.filter(customer=user, chef=OuterRef('pk'))
            ),
            is_favorite_value=Exists(
                Favorite.objects.filter(user=user, chef=OuterRef('pk'))
            ),
        )
    return queryset


class GovernorateListView(generics.ListAPIView):
    serializer_class = GovernorateSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Governorate.objects.filter(is_active=True).prefetch_related(
            'centers'
        ).order_by('-estimated_population', 'name_ar')


class SellerApplicationView(generics.CreateAPIView):
    serializer_class = SellerApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if hasattr(request.user, 'seller_profile'):
            return error_response('لقد قدمت طلب عامل بالفعل', status=400)
        response = super().create(request, *args, **kwargs)
        AuditLog.log_action(request.user, 'seller_account_activated', response.data, object_type='SellerProfile', object_id=str(response.data.get('id', '')))
        return success_response(data=response.data, message='تم تفعيل حساب العامل ويمكنك نشر خدماتك ومنتجاتك الآن')


class SellerPublicListView(generics.ListAPIView):
    serializer_class = SellerPublicSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'food_description']

    def get_queryset(self):
        queryset = public_seller_queryset(self.request.user)
        governorate = self.request.query_params.get('governorate')
        center = self.request.query_params.get('center')
        trade = self.request.query_params.get('trade')
        trade_category = self.request.query_params.get('trade_category')
        if governorate:
            queryset = queryset.filter(governorate__iexact=governorate)
        if center:
            queryset = queryset.filter(center__iexact=center)
        if trade:
            if connection.vendor == 'sqlite':
                matching_ids = [
                    seller.id for seller in queryset
                    if any(
                        item.get('trade') == trade
                        and (not trade_category or item.get('category') == trade_category)
                        for item in (seller.professions or [])
                    )
                ]
                queryset = queryset.filter(id__in=matching_ids)
            elif trade_category:
                queryset = queryset.filter(professions__contains=[{'trade': trade, 'category': trade_category}])
            else:
                queryset = queryset.filter(professions__contains=[{'trade': trade}])
        return queryset.order_by('name', 'id')

class SellerPublicDetailView(generics.RetrieveAPIView):
    serializer_class = SellerPublicSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return public_seller_queryset(self.request.user)


class SellerFollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses=SellerActionResultSerializer)
    def post(self, request, pk):
        chef = get_object_or_404(SellerProfile, pk=pk, approved='approved')
        if chef.user_id == request.user.id:
            return error_response('لا يمكنك متابعة حسابك', status=status.HTTP_400_BAD_REQUEST)
        _, created = Follower.objects.get_or_create(customer=request.user, chef=chef)
        return success_response(
            data={'following': True},
            message='تمت متابعة العامل' if created else '',
        )

    @extend_schema(request=None, responses=SellerActionResultSerializer)
    def delete(self, request, pk):
        Follower.objects.filter(customer=request.user, chef_id=pk).delete()
        return success_response(data={'following': False})


class SellerFavoriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses=SellerActionResultSerializer)
    def post(self, request, pk):
        chef = get_object_or_404(SellerProfile, pk=pk, approved='approved')
        _, created = Favorite.objects.get_or_create(user=request.user, chef=chef)
        return success_response(
            data={'favorite': True},
            message='تمت إضافة العامل إلى المفضلة' if created else '',
        )

    @extend_schema(request=None, responses=SellerActionResultSerializer)
    def delete(self, request, pk):
        Favorite.objects.filter(user=request.user, chef_id=pk).delete()
        return success_response(data={'favorite': False})



class SellerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = SellerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    http_method_names = ['get', 'patch']

    def get_object(self):
        return get_object_or_404(SellerProfile, user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_object()).data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=self.get_serializer(instance).data,
            message='تم تحديث صور وبيانات العامل',
        )


class SellerAdminListView(generics.ListAPIView):
    queryset = SellerProfile.objects.select_related('user').order_by('-created_at')
    serializer_class = SellerProfileSerializer
    permission_classes = [permissions.IsAdminUser]

    def list(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_queryset(), many=True).data)


class SellerApproveView(generics.UpdateAPIView):
    queryset = SellerProfile.objects.filter(approved='pending').select_related('user')
    serializer_class = SellerProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        profile = self.get_object()
        approved = request.data.get('approved', 'approved')
        if approved not in ['approved', 'rejected']:
            return error_response('حالة الموافقة غير صحيحة', status=400)
        profile.approved = approved
        profile.save(update_fields=['approved'])
        profile.user.role = 'seller' if profile.approved == 'approved' else 'user'
        profile.user.save(update_fields=['role'])
        Notification.objects.create(
            user=profile.user,
            title='تحديث طلب العامل',
            content='تم قبول طلبك كعامل' if approved == 'approved' else 'تم رفض طلبك كعامل',
            notification_type='seller_approval',
        )
        AuditLog.log_action(request.user, 'seller_profile_approved' if approved == 'approved' else 'seller_profile_rejected', {'seller_id': profile.id}, object_type='SellerProfile', object_id=str(profile.id))
        return success_response(data=self.get_serializer(profile).data, message='تم تحديث حالة العامل')
