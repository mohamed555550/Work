from django.contrib import admin
from .models import SellerProfile


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'governorate', 'center', 'approved', 'created_at')
    list_filter = ('approved', 'governorate', 'center')
    search_fields = ('name', 'user__username', 'governorate', 'center')
