from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'category', 'price', 'preparation_time', 'created_at')
    list_filter = ('category', 'seller__approved')
    search_fields = ('name', 'seller__name')
