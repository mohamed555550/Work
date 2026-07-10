from django.utils import timezone

from .models import Chat, ChatMessage


def get_or_create_order_chat(order):
    chat, _ = Chat.objects.get_or_create(
        order=order,
        defaults={
            'customer': order.user,
            'chef': order.seller,
        },
    )
    return chat


def mark_messages_read(chat, user):
    now = timezone.now()
    message_ids = list(
        ChatMessage.objects.filter(
            chat=chat,
            read_at__isnull=True,
        ).exclude(sender=user).values_list('id', flat=True)
    )
    if message_ids:
        ChatMessage.objects.filter(id__in=message_ids).update(read_at=now)
    return message_ids, now
