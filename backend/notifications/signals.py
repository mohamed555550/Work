import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Notification
from .push import send_push_notification

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Notification)
def broadcast_notification(sender, instance, created, **kwargs):
    if not created:
        return
    def publish():
        try:
            async_to_sync(get_channel_layer().group_send)(
                f'notifications_{instance.user_id}',
                {
                    'type': 'notification.message',
                    'notification': {
                        'id': instance.id,
                        'title': instance.title,
                        'content': instance.content,
                        'notification_type': instance.notification_type,
                        'read': instance.read,
                        'order': instance.order_id,
                        'created_at': instance.created_at.isoformat(),
                    },
                },
            )
            send_push_notification(instance)
        except Exception:
            logger.exception('Failed to publish notification %s', instance.id)

    transaction.on_commit(publish)
