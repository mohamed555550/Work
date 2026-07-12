import json
import logging

from django.conf import settings

from .models import PushSubscription

logger = logging.getLogger(__name__)


def send_push_notification(notification):
    public_key = getattr(settings, 'WEB_PUSH_PUBLIC_KEY', '')
    private_key = getattr(settings, 'WEB_PUSH_PRIVATE_KEY', '')
    if not public_key or not private_key:
        return

    try:
        from pywebpush import WebPushException, webpush
    except Exception:
        logger.warning('pywebpush is not installed; skipping push notifications')
        return

    payload = json.dumps({
        'title': notification.title,
        'body': notification.content,
        'url': f"/chat/{notification.order_id}" if notification.order_id else '/notifications',
        'notification_id': notification.id,
        'type': notification.notification_type,
    })
    subscriptions = PushSubscription.objects.filter(user=notification.user)
    for subscription in subscriptions:
        try:
            webpush(
                subscription_info={
                    'endpoint': subscription.endpoint,
                    'keys': {
                        'p256dh': subscription.p256dh,
                        'auth': subscription.auth,
                    },
                },
                data=payload,
                vapid_private_key=private_key,
                vapid_claims={'sub': getattr(settings, 'WEB_PUSH_SUBJECT', 'mailto:admin@sanay3y.local')},
            )
        except WebPushException as exc:
            status_code = getattr(getattr(exc, 'response', None), 'status_code', None)
            if status_code in {404, 410}:
                subscription.delete()
                continue
            logger.exception('Failed to send push notification %s', notification.id)
        except Exception:
            logger.exception('Failed to send push notification %s', notification.id)
