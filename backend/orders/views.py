from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.views import APIView
from .models import Order, ServiceRequest, ServiceRequestImage
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusSerializer,
    ServiceRequestSerializer,
    validate_service_request_images,
)
from common.throttles import OrderCreationThrottle
from common.utils import success_response, error_response
from audit_logs.models import AuditLog
from notifications.models import Notification
from chat.services import get_or_create_order_chat


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [OrderCreationThrottle]

    def create(self, request, *args, **kwargs):
        if request.user.role not in ['user', 'seller']:
            return error_response('غير مصرح', status=403)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return success_response(data=OrderSerializer(order).data, message='تم إنشاء الطلب بنجاح')


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.select_related('seller__user', 'user').prefetch_related('items__product')
        if self.request.user.is_staff:
            return queryset
        if self.request.user.role == 'seller' and hasattr(self.request.user, 'seller_profile'):
            return queryset.filter(seller=self.request.user.seller_profile)
        return queryset.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_queryset(), many=True).data)


class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.select_related('seller__user', 'user').prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()
        if not request.user.is_staff and order.user != request.user and order.seller.user != request.user:
            return error_response('غير مصرح', status=403)
        return success_response(data=self.get_serializer(order).data)


class OrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.select_related('seller__user', 'user')
    serializer_class = OrderStatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        if not request.user.is_staff and order.seller.user != request.user:
            return error_response('غير مصرح', status=403)
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        Notification.objects.create(
            user=order.user,
            title='تحديث حالة الطلب',
            content=f'طلبك رقم {order.id} تم تحديثه إلى {order.get_status_display()}',
            notification_type='order_update',
            order=order,
        )
        AuditLog.log_action(request.user, 'order_status_changed', {'order_id': order.id, 'status': order.status}, object_type='Order', object_id=str(order.id))
        return success_response(data=OrderSerializer(order).data, message='تم تحديث حالة الطلب')


class OrderCancelView(generics.UpdateAPIView):
    queryset = Order.objects.select_related('seller__user', 'user')
    serializer_class = OrderStatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        if order.user != request.user:
            return error_response('غير مصرح', status=403)
        if not order.can_be_canceled():
            return error_response('لا يمكن إلغاء الطلب بعد بدء التحضير', status=400)
        order.status = 'canceled'
        order.save(update_fields=['status'])
        Notification.objects.create(
            user=request.user,
            title='تم إلغاء الطلب',
            content=f'طلبك رقم {order.id} تم إلغاؤه',
            notification_type='order_update',
            order=order,
        )
        AuditLog.log_action(request.user, 'order_canceled', {'order_id': order.id}, object_type='Order', object_id=str(order.id))
        return success_response(data=OrderSerializer(order).data, message='تم إلغاء الطلب')


class ServiceRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = ServiceRequest.objects.select_related('customer').prefetch_related('images', 'orders')
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(customer=self.request.user)

    def list(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_queryset(), many=True).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        files = list(request.FILES.getlist('images')) + list(request.FILES.getlist('images[]'))
        validate_service_request_images(files)
        service_request = serializer.save()
        for index, upload in enumerate(files):
            ServiceRequestImage.objects.create(request=service_request, image=upload, sort_order=index)
        return success_response(
            data=self.get_serializer(service_request).data,
            message='تم نشر طلب المشكلة بنجاح',
            status=201,
        )


class OpenServiceRequestListView(generics.ListAPIView):
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not hasattr(self.request.user, 'seller_profile'):
            return ServiceRequest.objects.none()
        profile = self.request.user.seller_profile
        queryset = (
            ServiceRequest.objects
            .filter(status='open', governorate__iexact=profile.governorate)
            .select_related('customer')
            .prefetch_related('images', 'orders')
        )
        if profile.center:
            queryset = queryset.filter(center__iexact=profile.center)
        professions = profile.professions or []
        trades = {item.get('trade') for item in professions if isinstance(item, dict) and item.get('trade')}
        categories = {item.get('category') for item in professions if isinstance(item, dict) and item.get('category')}
        if trades:
            queryset = queryset.filter(Q(trade='') | Q(trade='all') | Q(trade__in=trades))
        if categories:
            queryset = queryset.filter(Q(trade_category='') | Q(trade_category='all') | Q(trade_category__in=categories))
        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_queryset(), many=True).data)


class ServiceRequestChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if not hasattr(request.user, 'seller_profile'):
            return error_response('يجب تسجيل الدخول كصنايعي للتواصل مع العميل', status=403)
        service_request = get_object_or_404(
            ServiceRequest.objects.select_related('customer'),
            pk=pk,
            status='open',
        )
        seller = request.user.seller_profile
        if service_request.customer_id == request.user.id:
            return error_response('لا يمكنك التواصل مع طلبك من نفس الحساب', status=400)
        order = Order.objects.filter(
            user=service_request.customer,
            seller=seller,
            service_request=service_request,
        ).order_by('-created_at').first()
        if not order:
            order = Order.objects.create(
                user=service_request.customer,
                seller=seller,
                service_request=service_request,
                total_price=0,
                pickup_address=f'{service_request.governorate} - {service_request.center}',
            )
            Notification.objects.create(
                user=service_request.customer,
                title='صنايعي عايز يتواصل معاك',
                content=f'{seller.name} فتح محادثة بخصوص: {service_request.title}',
                notification_type='message',
                order=order,
            )
        chat = get_or_create_order_chat(order)
        return success_response(data={'chat_id': chat.id, 'order_id': order.id})
