from django.contrib import admin
from .models import ChatMessage, SupportConversation, SupportMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('order', 'sender', 'created_at')
    search_fields = ('order__id', 'sender__username', 'message')


@admin.register(SupportConversation)
class SupportConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'updated_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email')


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'created_at', 'read_at')
    search_fields = ('conversation__user__username', 'sender__username', 'message')
