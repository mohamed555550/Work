from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from datetime import timedelta


class Chat(models.Model):
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='chat')
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_chats'
    )
    chef = models.ForeignKey('sellers.SellerProfile', on_delete=models.CASCADE, related_name='chats')
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chats'
        indexes = [
            models.Index(fields=['customer', '-updated_at'], name='chat_customer_time_idx'),
            models.Index(fields=['chef', '-updated_at'], name='chat_chef_time_idx'),
        ]

    def __str__(self):
        return f'Conversation for order {self.order_id}'


class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='messages')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    message = models.TextField(blank=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    image = models.ImageField(
        upload_to='chat/images/%Y/%m/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'gif'])],
    )
    video = models.FileField(
        upload_to='chat/videos/%Y/%m/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['mp4', 'webm', 'mov'])],
    )
    reply_to = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies'
    )
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    deleted_for = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='hidden_chat_messages'
    )
    deleted_for_everyone_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['order', 'created_at'], name='chat_order_time_idx'),
            models.Index(fields=['chat', 'created_at'], name='message_chat_time_idx'),
            models.Index(fields=['chat', 'read_at'], name='message_chat_unread_idx'),
        ]

    def __str__(self):
        return f'Chat message by {self.sender.username}'

    def can_delete_for_everyone(self):
        return (
            self.deleted_for_everyone_at is None
            and timezone.now() <= self.created_at + timedelta(minutes=15)
        )


class SupportConversation(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_conversation',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'support_conversations'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['status', '-updated_at'], name='support_status_time_idx'),
        ]

    def __str__(self):
        return f'Sanati support conversation with {self.user.username}'


class SupportMessage(models.Model):
    conversation = models.ForeignKey(
        SupportConversation,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_support_messages',
    )
    message = models.TextField(max_length=4000)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'support_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(
                fields=['conversation', 'created_at'],
                name='support_message_time_idx',
            ),
            models.Index(
                fields=['conversation', 'read_at'],
                name='support_message_read_idx',
            ),
        ]

    def __str__(self):
        return f'Support message by {self.sender.username}'


class Message(ChatMessage):
    """Canonical domain name; ChatMessage remains for API compatibility."""

    class Meta:
        proxy = True

