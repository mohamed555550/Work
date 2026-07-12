from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('unit_price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'seller', 'status', 'total_price', 'platform_fee',
        'seller_earnings', 'created_at',
    )
    readonly_fields = ('commission_rate', 'platform_fee', 'seller_earnings')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username', 'seller__name', 'idempotency_key')
    inlines = [OrderItemInline]
