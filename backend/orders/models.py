from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import models
from django.utils import timezone


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('confirmed_by_seller', 'تم التأكيد من العامل'),
        ('preparing', 'قيد التحضير'),
        ('ready_for_pickup', 'جاهز للاستلام'),
        ('completed', 'مكتمل'),
        ('canceled', 'ملغي'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    seller = models.ForeignKey('sellers.SellerProfile', on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'))
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    seller_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    pickup_time = models.DateTimeField(default=timezone.now)
    pickup_address = models.CharField(max_length=500, default='')
    service_request = models.ForeignKey(
        'orders.ServiceRequest',
        on_delete=models.SET_NULL,
        related_name='orders',
        blank=True,
        null=True,
    )
    idempotency_key = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', '-created_at'], name='order_customer_idx'),
            models.Index(fields=['seller', 'status', '-created_at'], name='order_seller_idx'),
        ]
        constraints = [
            models.UniqueConstraint(fields=['user', 'idempotency_key'], name='unique_order_key_per_user'),
            models.CheckConstraint(condition=models.Q(platform_fee__gte=0), name='order_platform_fee_nonnegative'),
            models.CheckConstraint(condition=models.Q(seller_earnings__gte=0), name='order_seller_earnings_nonnegative'),
        ]

    def calculate_financials(self):
        rate = Decimal(str(getattr(settings, 'PLATFORM_COMMISSION_RATE', '10.00')))
        total = Decimal(self.total_price or 0)
        self.commission_rate = rate
        self.platform_fee = (
            total * rate / Decimal('100')
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.seller_earnings = total - self.platform_fee

    def save(self, *args, **kwargs):
        if self._state.adding and not self.platform_fee and not self.seller_earnings:
            self.calculate_financials()
        super().save(*args, **kwargs)

    def can_be_canceled(self):
        return self.status in ['pending', 'confirmed_by_seller']

    def is_final(self):
        return self.status in ['completed', 'canceled']

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_items'
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gt=0), name='order_item_quantity_positive'),
            models.CheckConstraint(condition=models.Q(unit_price__gte=0), name='order_item_price_nonnegative'),
        ]

    @property
    def total_price(self):
        return self.unit_price * self.quantity


class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In progress'),
        ('closed', 'Closed'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_requests')
    title = models.CharField(max_length=160)
    description = models.TextField(max_length=2000)
    governorate = models.CharField(max_length=120)
    center = models.CharField(max_length=120)
    trade = models.CharField(max_length=80, blank=True, default='')
    trade_category = models.CharField(max_length=80, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'service_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'governorate', 'center', '-created_at'], name='service_req_location_idx'),
            models.Index(fields=['customer', 'status', '-created_at'], name='service_req_customer_idx'),
        ]

    def __str__(self):
        return f'{self.title} by {self.customer.username}'


class ServiceRequestImage(models.Model):
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='service-requests/images/')
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'service_request_images'
        ordering = ['sort_order', 'id']
        indexes = [
            models.Index(fields=['request', 'sort_order'], name='service_req_image_sort_idx'),
        ]
