from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase, override_settings
from django.urls import path
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async
from common.websocket_auth import JwtAuthMiddleware
from users.models import User
from .consumers import NotificationConsumer
from .models import Notification


application = JwtAuthMiddleware(URLRouter([
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]))


@override_settings(CHANNEL_LAYERS={'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}})
class NotificationWebSocketTests(TransactionTestCase):
    async def test_authenticated_user_receives_realtime_notification(self):
        user = await database_sync_to_async(User.objects.create_user)(
            username='socket-user',
            email='socket@example.com',
            password='Password123!',
            email_verified=True,
        )
        token = str(AccessToken.for_user(user))
        communicator = WebsocketCommunicator(
            application,
            '/ws/notifications/',
            subprotocols=['access_token', token],
        )
        connected, selected_protocol = await communicator.connect()
        self.assertTrue(connected)
        self.assertEqual(selected_protocol, 'access_token')

        await database_sync_to_async(Notification.objects.create)(
            user=user,
            title='اختبار',
            content='إشعار فوري',
            notification_type='message',
        )
        payload = await communicator.receive_json_from(timeout=2)
        self.assertEqual(payload['type'], 'notification.message')
        self.assertEqual(payload['data']['title'], 'اختبار')
        await communicator.disconnect()

    async def test_anonymous_connection_is_rejected(self):
        communicator = WebsocketCommunicator(application, '/ws/notifications/')
        connected, close_code = await communicator.connect()
        self.assertFalse(connected)
        self.assertEqual(close_code, 4401)
