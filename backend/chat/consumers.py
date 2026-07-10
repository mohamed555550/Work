from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.cache import cache
from django.utils import timezone

from notifications.models import Notification
from orders.models import Order
from sellers.models import SellerProfile
from users.models import User
from .models import ChatMessage
from .services import get_or_create_order_chat, mark_messages_read


class OrderChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.group_name = f'order_chat_{self.order_id}'
        user = self.scope['user']
        if not user.is_authenticated or not await self._can_access(user.id, user.is_staff):
            await self.close(code=4403)
            return
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self._set_presence(user.id, True)
        await self.accept(
            subprotocol='access_token'
            if 'access_token' in self.scope.get('subprotocols', [])
            else None
        )
        await self.channel_layer.group_send(
            self.group_name,
            {'type': 'chat.presence', 'user_id': user.id, 'online': True},
        )
        delivered_ids, delivered_at = await self._mark_all_delivered(user.id)
        if delivered_ids:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat.status',
                    'message_ids': delivered_ids,
                    'status': 'delivered',
                    'timestamp': delivered_at,
                },
            )

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            user = self.scope.get('user')
            if user and user.is_authenticated:
                is_offline, last_seen = await self._set_presence(user.id, False)
                if is_offline:
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'chat.presence',
                            'user_id': user.id,
                            'online': False,
                            'last_seen_at': last_seen,
                        },
                    )
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        action = content.get('action', 'send')
        user = self.scope['user']
        if action == 'typing':
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat.typing',
                    'user_id': user.id,
                    'typing': bool(content.get('typing')),
                },
            )
            return
        if action == 'read':
            message_ids, read_at = await self._mark_read(user.id)
            if message_ids:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'chat.status',
                        'message_ids': message_ids,
                        'status': 'seen',
                        'timestamp': read_at,
                    },
                )
            return
        if action != 'send':
            await self.send_json({'type': 'error', 'error': 'إجراء غير مدعوم'})
            return

        message = str(content.get('message', '')).strip()
        if not message or len(message) > 2000:
            await self.send_json({'type': 'error', 'error': 'الرسالة غير صالحة'})
            return
        reply_to = content.get('reply_to')
        created = await self._create_message(user.id, message, reply_to)
        if not created:
            await self.send_json({'type': 'error', 'error': 'الرسالة المشار إليها غير صالحة'})

    async def chat_message(self, event):
        if event['message']['sender'] != self.scope['user'].id:
            delivered_at = await self._mark_delivered(event['message']['id'])
            if delivered_at:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'chat.status',
                        'message_ids': [event['message']['id']],
                        'status': 'delivered',
                        'timestamp': delivered_at,
                    },
                )
        await self.send_json({'type': 'chat.message', 'data': event['message']})

    async def chat_status(self, event):
        await self.send_json({
            'type': 'chat.status',
            'message_ids': event['message_ids'],
            'status': event['status'],
            'timestamp': event['timestamp'],
        })

    async def chat_typing(self, event):
        if event['user_id'] != self.scope['user'].id:
            await self.send_json({
                'type': 'chat.typing',
                'user_id': event['user_id'],
                'typing': event['typing'],
            })

    async def chat_presence(self, event):
        if event['user_id'] != self.scope['user'].id:
            await self.send_json({
                'type': 'chat.presence',
                'user_id': event['user_id'],
                'online': event['online'],
                'last_seen_at': event.get('last_seen_at'),
            })

    async def chat_deleted(self, event):
        await self.send_json({
            'type': 'chat.deleted',
            'message_id': event['message_id'],
            'scope': event['scope'],
        })

    @database_sync_to_async
    def _can_access(self, user_id, is_staff):
        if is_staff:
            return Order.objects.filter(pk=self.order_id).exists()
        return Order.objects.filter(pk=self.order_id).filter(
            user_id=user_id
        ).exists() or Order.objects.filter(
            pk=self.order_id,
            seller__user_id=user_id,
        ).exists()

    @database_sync_to_async
    def _create_message(self, user_id, message, reply_to_id):
        order = Order.objects.select_related('user', 'seller__user').get(pk=self.order_id)
        chat = get_or_create_order_chat(order)
        reply_to = None
        if reply_to_id:
            reply_to = ChatMessage.objects.filter(pk=reply_to_id, chat=chat).first()
            if not reply_to:
                return False
        ChatMessage.objects.create(
            order=order,
            chat=chat,
            sender_id=user_id,
            message=message,
            reply_to=reply_to,
        )
        recipient = order.seller.user if order.user_id == user_id else order.user
        Notification.objects.create(
            user=recipient,
            title='رسالة جديدة',
            content=f'لديك رسالة جديدة بخصوص الطلب رقم {order.id}',
            notification_type='message',
            order=order,
        )
        return True

    @database_sync_to_async
    def _mark_delivered(self, message_id):
        now = timezone.now()
        updated = ChatMessage.objects.filter(
            pk=message_id,
            delivered_at__isnull=True,
        ).exclude(sender_id=self.scope['user'].id).update(delivered_at=now)
        return now.isoformat() if updated else None

    @database_sync_to_async
    def _mark_all_delivered(self, user_id):
        now = timezone.now()
        ids = list(
            ChatMessage.objects.filter(
                order_id=self.order_id,
                delivered_at__isnull=True,
            ).exclude(sender_id=user_id).values_list('id', flat=True)
        )
        if ids:
            ChatMessage.objects.filter(id__in=ids).update(delivered_at=now)
        return ids, now.isoformat()

    @database_sync_to_async
    def _mark_read(self, user_id):
        order = Order.objects.select_related('user', 'seller').get(pk=self.order_id)
        chat = get_or_create_order_chat(order)
        ids, timestamp = mark_messages_read(chat, User.objects.get(pk=user_id))
        return ids, timestamp.isoformat()

    @database_sync_to_async
    def _set_presence(self, user_id, online):
        key = f'chat_presence:{user_id}'
        now = timezone.now()
        if online:
            count = int(cache.get(key, 0)) + 1
            cache.set(key, count, timeout=60 * 60 * 24)
            User.objects.filter(pk=user_id).update(is_online=True)
            SellerProfile.objects.filter(user_id=user_id).update(is_online=True)
            return False, None
        count = max(int(cache.get(key, 1)) - 1, 0)
        if count:
            cache.set(key, count, timeout=60 * 60 * 24)
            return False, None
        cache.delete(key)
        User.objects.filter(pk=user_id).update(is_online=False, last_seen_at=now)
        SellerProfile.objects.filter(user_id=user_id).update(
            is_online=False,
            last_seen_at=now,
        )
        return True, now.isoformat()
