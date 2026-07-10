from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Suggestion, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Marketplace', {'fields': ('role', 'email_verified', 'profile_image')}),
    )
    list_display = ('username', 'email', 'role', 'email_verified', 'is_staff', 'is_active')
    list_filter = ('role', 'email_verified', 'is_staff', 'is_active')


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'status', 'created_at', 'email_sent_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'message', 'user__username', 'user__email')
    readonly_fields = ('user', 'subject', 'message', 'status', 'email_sent_at', 'email_error', 'created_at')
