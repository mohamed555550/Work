from rest_framework import generics, permissions
from .models import Order
from .serializers import OrderCreateSerializer, OrderSerializer, OrderStatusSerializer
from common.throttles import OrderCreationThrottle
from common.utils import success_response, error_response
from audit_logs.models import AuditLog
from notifications.models import Notification


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
