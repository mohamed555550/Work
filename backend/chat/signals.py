import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Chat, ChatMessage

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=ChatMessage)
def normalize_message(sender, instance, **kwargs):
    instance.message = (instance.message or '').strip()


@receiver(post_save, sender=ChatMessage)
def broadcast_chat_message(sender, instance, created, **kwargs):
    if not created:
        return

    def publish():
        try:
            if instance.chat_id:
                Chat.objects.filter(pk=instance.chat_id).update(updated_at=timezone.now())
            reply = instance.reply_to
            async_to_sync(get_channel_layer().group_send)(
                f'order_chat_{instance.order_id}',
                {
                    'type': 'chat.message',
                    'message': {
                        'id': instance.id,
                        'order': instance.order_id,
                        'chat': instance.chat_id,
                        'sender': instance.sender_id,
                        'sender_name': instance.sender.username,
                        'message': instance.message,
                        'message_type': instance.message_type,
                        'image': instance.image.url if instance.image else None,
                        'video': instance.video.url if instance.video else None,
                        'reply': {
                            'id': reply.id,
                            'sender_name': reply.sender.username,
                            'message': reply.message,
                            'message_type': reply.message_type,
                        } if reply else None,
                        'status': 'sent',
                        'is_deleted': False,
                        'can_delete_for_everyone': True,
                        'delivered_at': None,
                        'read_at': None,
                        'created_at': instance.created_at.isoformat(),
                    },
                },
            )
        except Exception:
            logger.exception('Failed to publish chat message %s', instance.id)

    transaction.on_commit(publish)
