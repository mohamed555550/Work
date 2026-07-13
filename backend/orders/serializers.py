from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers
from .models import Order, OrderItem, ServiceRequest, ServiceRequestImage
from products.models import Product
from audit_logs.models import AuditLog
from notifications.models import Notification
from cart.models import CartItem


MAX_SERVICE_REQUEST_IMAGES = 12
MAX_SERVICE_REQUEST_IMAGE_SIZE = 10 * 1024 * 1024
SERVICE_REQUEST_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}


class ServiceRequestImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequestImage
        fields = ['id', 'image', 'sort_order', 'created_at']
        read_only_fields = fields


class ServiceRequestSerializer(serializers.ModelSerializer):
    images = ServiceRequestImageSerializer(many=True, read_only=True)
    customer_name = serializers.SerializerMethodField()
    chat_order_ids = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'title', 'description', 'governorate', 'center',
            'trade', 'trade_category', 'status', 'customer_name',
            'images', 'chat_order_ids', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'customer_name', 'images', 'chat_order_ids', 'created_at', 'updated_at']

    def get_customer_name(self, obj):
        return obj.customer.get_full_name() or obj.customer.username

    def get_chat_order_ids(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return []
        orders = obj.orders.all()
        if request.user.role == 'seller' and hasattr(request.user, 'seller_profile'):
            orders = orders.filter(seller=request.user.seller_profile)
        elif not request.user.is_staff:
            orders = orders.filter(user=request.user)
        return list(orders.values_list('id', flat=True))

    def validate_title(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError('اكتب عنوانا أوضح للمشكلة')
        return value

    def validate_description(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError('اكتب وصفا أوضح للمشكلة')
        return value

    def create(self, validated_data):
        return ServiceRequest.objects.create(customer=self.context['request'].user, **validated_data)


def validate_service_request_images(files):
    if len(files) > MAX_SERVICE_REQUEST_IMAGES:
        raise serializers.ValidationError({'images': f'يمكن رفع حتى {MAX_SERVICE_REQUEST_IMAGES} صورة في الطلب الواحد'})
    for upload in files:
        if upload.size > MAX_SERVICE_REQUEST_IMAGE_SIZE:
            raise serializers.ValidationError({'images': 'حجم كل صورة يجب ألا يتجاوز 10 ميجابايت'})
        if getattr(upload, 'content_type', '') not in SERVICE_REQUEST_IMAGE_TYPES:
            raise serializers.ValidationError({'images': 'صيغة الصور يجب أن تكون JPG أو PNG أو WebP أو GIF'})


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_image = serializers.ImageField(source='product.image', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 'quantity', 'unit_price']
        read_only_fields = ['unit_price', 'product_name', 'product_image']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('الكمية يجب أن تكون 1 على الأقل')
        return value


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    idempotency_key = serializers.CharField(required=False, allow_blank=True)
    pickup_time = serializers.DateTimeField(required=True)

    class Meta:
        model = Order
        fields = ['idempotency_key', 'pickup_time', 'items']

    def validate(self, attrs):
        if 'delivery_type' in self.initial_data:
            raise serializers.ValidationError({'delivery_type': 'خدمة التوصيل غير متاحة؛ الطلبات للاستلام فقط'})
        pickup_time = attrs.get('pickup_time')
        if pickup_time and pickup_time <= timezone.now():
            raise serializers.ValidationError({'pickup_time': 'اختر موعد استلام في المستقبل'})
        return attrs

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('يجب إضافة عناصر إلى الطلب')
        product_ids = [item['product'].id for item in value]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError('لا يمكن تكرار نفس المنتج داخل الطلب')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        items_data = validated_data.pop('items')
        idempotency_key = validated_data.get('idempotency_key') or None
        pickup_time = validated_data.pop('pickup_time')

        if idempotency_key:
            existing = Order.objects.filter(idempotency_key=idempotency_key, user=user).first()
            if existing:
                return existing

        product_ids = [item['product'].id for item in items_data]
        products = list(Product.objects.select_related('seller').filter(
            id__in=product_ids,
            seller__approved='approved',
        ).filter(
            Q(is_available=True) | Q(available_at__lte=timezone.now()),
        ))
        products_by_id = {product.id: product for product in products}
        if len(products_by_id) != len(product_ids):
            raise serializers.ValidationError('يوجد منتج غير متاح في الطلب')

        seller = products[0].seller
        if any(product.seller_id != seller.id for product in products):
            raise serializers.ValidationError('يجب أن تكون كل المنتجات من نفس العامل')
        if not seller.is_active_seller:
            raise serializers.ValidationError('العامل غير متاح حالياً')
        if seller.user_id == user.id:
            raise serializers.ValidationError('لا يمكنك طلب منتجاتك من حسابك نفسه')
        if not seller.pickup_address.strip():
            raise serializers.ValidationError('العامل لم يحدد عنوان الاستلام بعد')
        minimum_pickup_time = timezone.now() + timedelta(
            minutes=max(product.preparation_time for product in products)
        )
        if pickup_time < minimum_pickup_time:
            raise serializers.ValidationError({
                'pickup_time': 'موعد الاستلام لا يكفي لتجهيز المنتجات أو الخدمة',
            })

        total_price = sum(products_by_id[item['product'].id].price * item['quantity'] for item in items_data)

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=user,
                    seller=seller,
                    total_price=total_price,
                    idempotency_key=idempotency_key,
                    pickup_time=pickup_time,
                    pickup_address=seller.pickup_address,
                )
                for item in items_data:
                    product = products_by_id[item['product'].id]
                    OrderItem.objects.create(order=order, product=product, quantity=item['quantity'], unit_price=product.price)
                Notification.objects.create(
                    user=user,
                    title='تم إنشاء الطلب',
                    content=f'طلبك رقم {order.id} قيد الانتظار',
                    notification_type='order_update',
                    order=order,
                )
                Notification.objects.create(
                    user=seller.user,
                    title='طلب جديد',
                    content=(
                        f'طلب جديد رقم {order.id} من '
                        f'{user.get_full_name() or user.username} بقيمة {total_price} ج.م. '
                        'افتح الإشعار لمراجعة الطلب والتواصل مع العميل.'
                    ),
                    notification_type='order_update',
                    order=order,
                )
                AuditLog.log_action(user, 'order_created', {'order_id': order.id, 'total_price': str(total_price)}, object_type='Order', object_id=str(order.id))
                CartItem.objects.filter(user=user, product_id__in=product_ids).delete()
        except IntegrityError:
            if idempotency_key:
                return Order.objects.get(idempotency_key=idempotency_key, user=user)
            raise
        return order


class OrderItemReadSerializer(OrderItemSerializer):
    class Meta(OrderItemSerializer.Meta):
        fields = OrderItemSerializer.Meta.fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True)
    seller_name = serializers.ReadOnlyField(source='seller.name')
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Order
        fields = [
            'id', 'seller_name', 'user_name', 'total_price', 'commission_rate',
            'platform_fee', 'seller_earnings', 'status', 'items', 'created_at',
            'updated_at', 'pickup_time', 'pickup_address',
        ]


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        order = self.instance
        if order.is_final():
            raise serializers.ValidationError('لا يمكن تحديث حالة طلب منتهي')
        allowed = {
            'pending': ['confirmed_by_seller', 'canceled'],
            'confirmed_by_seller': ['preparing', 'canceled'],
            'preparing': ['ready_for_pickup'],
            'ready_for_pickup': ['completed'],
        }
        if value not in allowed.get(order.status, []):
            raise serializers.ValidationError('تغيير الحالة غير مسموح')
        return value
