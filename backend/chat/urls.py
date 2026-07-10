from django.urls import path
from .views import (
    ChatCreateView,
    ChatListView,
    ConversationListView,
    DeleteMessageView,
    AdminSupportConversationDetailView,
    AdminSupportConversationListView,
    MarkChatReadView,
    OwnSupportConversationView,
    StartChefChatView,
    SupportMessageCreateView,
)

urlpatterns = [
    path('conversations/', ConversationListView.as_view(), name='conversation_list'),
    path('order/<int:order_id>/', ChatListView.as_view(), name='chat_list'),
    path('order/<int:order_id>/read/', MarkChatReadView.as_view(), name='chat_mark_read'),
    path('send/', ChatCreateView.as_view(), name='chat_send'),
    path('messages/<int:pk>/', DeleteMessageView.as_view(), name='chat_message_delete'),
    path('with-chef/<int:chef_id>/', StartChefChatView.as_view(), name='chat_with_chef'),
    path('support/', OwnSupportConversationView.as_view(), name='support_conversation'),
    path('support/messages/', SupportMessageCreateView.as_view(), name='support_message_create'),
    path('support/conversations/', AdminSupportConversationListView.as_view(), name='support_conversation_list'),
    path('support/conversations/<int:pk>/', AdminSupportConversationDetailView.as_view(), name='support_conversation_detail'),
]
