from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.test import TransactionTestCase
from rest_framework_simplejwt.tokens import AccessToken

from common.websocket_auth import JwtAuthMiddleware
from foodmarket.routing import websocket_urlpatterns
from notifications.models import Notification
from orders.models import Order
from sellers.models import SellerProfile
from users.models import User
from .models import Chat, ChatMessage, SupportConversation, SupportMessage


class MessagingApiTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer-chat',
            email='customer-chat@example.com',
            password='Password123!',
            email_verified=True,
        )
        chef_user = User.objects.create_user(
            username='chef-chat',
            email='chef-chat@example.com',
            password='Password123!',
            role='seller',
            email_verified=True,
        )
        self.chef = SellerProfile.objects.create(
            user=chef_user,
            name='ظ…ط·ط¨ط® ط§ظ„ط±ط³ط§ط¦ظ„',
            governorate='ط§ظ„ظ…ظ†ظٹط§',
            center='ظ…ط±ظƒط² ط§ظ„ظ…ظ†ظٹط§',
            food_description='ط·ط¹ط§ظ… ظ…ظ†ط²ظ„ظٹ',
            approved='approved',
        )
        self.order = Order.objects.create(
            user=self.customer,
            seller=self.chef,
            total_price=100,
        )
        self.client.force_authenticate(self.customer)

    def send_text(self, text='ط£ظ‡ظ„ظ‹ط§', reply_to=None):
        payload = {'order': self.order.id, 'message': text}
        if reply_to:
            payload['reply_to'] = reply_to
        return self.client.post(reverse('chat_send'), payload)

    def test_creates_one_conversation_per_order_and_supports_reply(self):
        first = self.send_text()
        second = self.send_text('ط±ط¯ ط¬ط¯ظٹط¯', first.data['data']['id'])

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Chat.objects.filter(order=self.order).count(), 1)
        self.assertEqual(second.data['data']['reply']['id'], first.data['data']['id'])

    def test_video_upload_and_conversation_search(self):
        video = SimpleUploadedFile(
            'meal.mp4',
            b'fake-video-content',
            content_type='video/mp4',
        )
        response = self.client.post(
            reverse('chat_send'),
            {'order': self.order.id, 'video': video},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['message_type'], 'video')

        conversations = self.client.get(
            reverse('conversation_list'),
            {'search': 'ظ…ط·ط¨ط® ط§ظ„ط±ط³ط§ط¦ظ„'},
        )
        self.assertEqual(conversations.status_code, status.HTTP_200_OK)
        self.assertEqual(conversations.data['count'], 1)

    def test_read_receipt_and_delete_scopes(self):
        message = ChatMessage.objects.create(
            order=self.order,
            chat=Chat.objects.create(
                order=self.order,
                customer=self.customer,
                chef=self.chef,
            ),
            sender=self.chef.user,
            message='ط±ط³ط§ظ„ط© ظˆط§ط±ط¯ط©',
        )
        read_response = self.client.post(reverse('chat_mark_read', args=[self.order.id]))
        message.refresh_from_db()
        self.assertEqual(read_response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(message.delivered_at)
        self.assertIsNotNone(message.read_at)

        delete_response = self.client.delete(
            reverse('chat_message_delete', args=[message.id]) + '?scope=me'
        )
        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        listed = self.client.get(reverse('chat_list', args=[self.order.id]))
        self.assertEqual(listed.data['data'], [])

    def test_delete_for_everyone_is_limited_to_fifteen_minutes(self):
        response = self.send_text('ط±ط³ط§ظ„ط© ظ‚ط¯ظٹظ…ط©')
        message = ChatMessage.objects.get(pk=response.data['data']['id'])
        ChatMessage.objects.filter(pk=message.pk).update(
            created_at=timezone.now() - timedelta(minutes=16)
        )

        delete_response = self.client.delete(
            reverse('chat_message_delete', args=[message.id]) + '?scope=everyone'
        )

        self.assertEqual(delete_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_chef_profile_chat_uses_latest_existing_order(self):
        response = self.client.post(reverse('chat_with_chef', args=[self.chef.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['order_id'], self.order.id)
        self.assertEqual(Chat.objects.filter(order=self.order).count(), 1)

    def test_chef_profile_chat_requires_an_existing_order(self):
        other_customer = User.objects.create_user(
            username='new-customer',
            email='new-customer@example.com',
            password='Password123!',
        )
        self.client.force_authenticate(other_customer)

        response = self.client.post(reverse('chat_with_chef', args=[self.chef.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_phone_numbers_are_removed_from_rest_messages(self):
        response = self.send_text('ظƒظ„ظ…ظ†ظٹ ط¹ظ„ظ‰ 010-1234-5678 ط¨ط¹ط¯ طھط¬ظ‡ظٹط² ط§ظ„ط·ظ„ط¨')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        saved = ChatMessage.objects.get(pk=response.data['data']['id'])
        self.assertEqual(
            saved.message,
            'ظƒظ„ظ…ظ†ظٹ ط¹ظ„ظ‰ [طھظ… ط­ط°ظپ ط±ظ‚ظ… ط§ظ„ظ‡ط§طھظپ] ط¨ط¹ط¯ طھط¬ظ‡ظٹط² ط§ظ„ط·ظ„ط¨',
        )
        self.assertNotIn('010', response.data['data']['message'])

    def test_arabic_phone_digits_are_removed(self):
        response = self.send_text('ط±ظ‚ظ…ظٹ ظ ظ،ظ، ظ¢ظ£ظ¤ظ¥ ظ¦ظ§ظ¨ظ©')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['data']['message'],
            'ط±ظ‚ظ…ظٹ [طھظ… ط­ط°ظپ ط±ظ‚ظ… ط§ظ„ظ‡ط§طھظپ]',
        )


class SupportChatApiTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='support-customer',
            email='support-customer@example.com',
            password='Password123!',
            email_verified=True,
        )
        self.admin = User.objects.create_user(
            username='support-admin',
            email='support-admin@example.com',
            password='Password123!',
            role='admin',
            is_staff=True,
            email_verified=True,
        )

    def test_customer_can_open_support_and_send_complaint(self):
        self.client.force_authenticate(self.customer)

        detail = self.client.get(reverse('support_conversation'))
        response = self.client.post(
            reverse('support_message_create'),
            {'message': 'ط£ط±ظٹط¯ طھظ‚ط¯ظٹظ… ط´ظƒظˆظ‰ ط¨ط®طµظˆطµ ط·ظ„ط¨ظٹ'},
        )

        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conversation = SupportConversation.objects.get(user=self.customer)
        self.assertEqual(conversation.messages.count(), 1)
        self.assertEqual(
            SupportMessage.objects.get(conversation=conversation).sender,
            self.customer,
        )
        self.assertTrue(
            Notification.objects.filter(user=self.admin, title='ط±ط³ط§ظ„ط© ط¯ط¹ظ… ط¬ط¯ظٹط¯ط©').exists()
        )

    def test_admin_can_list_reply_and_close_conversation(self):
        conversation = SupportConversation.objects.create(user=self.customer)
        SupportMessage.objects.create(
            conversation=conversation,
            sender=self.customer,
            message='ظ…ط­طھط§ط¬ ظ…ط³ط§ط¹ط¯ط©',
        )
        self.client.force_authenticate(self.admin)

        conversations = self.client.get(reverse('support_conversation_list'))
        detail = self.client.get(
            reverse('support_conversation_detail', args=[conversation.id])
        )
        reply = self.client.post(
            reverse('support_message_create'),
            {'conversation_id': conversation.id, 'message': 'ط£ظ‡ظ„ظ‹ط§طŒ ط¨ظ†ط±ط§ط¬ط¹ ط´ظƒظˆطھظƒ ط§ظ„ط¢ظ†'},
        )
        close = self.client.patch(
            reverse('support_conversation_detail', args=[conversation.id]),
            {'status': 'closed'},
        )

        self.assertEqual(conversations.status_code, status.HTTP_200_OK)
        self.assertEqual(conversations.data['count'], 1)
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(reply.status_code, status.HTTP_201_CREATED)
        self.assertEqual(close.status_code, status.HTTP_200_OK)
        conversation.refresh_from_db()
        self.assertEqual(conversation.status, 'closed')
        self.assertTrue(
            Notification.objects.filter(
                user=self.customer,
                title='ط±ط¯ ط¬ط¯ظٹط¯ ظ…ظ† ط¯ط¹ظ… صنعتى',
            ).exists()
        )

    def test_customer_message_reopens_closed_conversation(self):
        conversation = SupportConversation.objects.create(
            user=self.customer,
            status='closed',
        )
        self.client.force_authenticate(self.customer)

        response = self.client.post(
            reverse('support_message_create'),
            {'message': 'ظ…ط§ ط²ظ„طھ ط£ط­طھط§ط¬ ظ„ظ„ظ…ط³ط§ط¹ط¯ط©'},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conversation.refresh_from_db()
        self.assertEqual(conversation.status, 'open')


class MessagingWebSocketTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.customer = User.objects.create_user(
            username='socket-customer',
            email='socket-customer@example.com',
            password='Password123!',
        )
        chef_user = User.objects.create_user(
            username='socket-chef',
            email='socket-chef@example.com',
            password='Password123!',
            role='seller',
        )
        chef = SellerProfile.objects.create(
            user=chef_user,
            name='ظ…ط·ط¨ط® ظ…ط¨ط§ط´ط±',
            governorate='ط§ظ„ظ…ظ†ظٹط§',
            center='ظ…ط±ظƒط² ط§ظ„ظ…ظ†ظٹط§',
            food_description='ط§ط®طھط¨ط§ط±',
            approved='approved',
        )
        self.chef_user = chef_user
        self.order = Order.objects.create(user=self.customer, seller=chef, total_price=50)

    def test_typing_and_message_are_broadcast_in_real_time(self):
        async_to_sync(self._websocket_scenario)()

    async def _websocket_scenario(self):
        websocket_application = JwtAuthMiddleware(URLRouter(websocket_urlpatterns))
        customer_socket = WebsocketCommunicator(
            websocket_application,
            f'/ws/orders/{self.order.id}/chat/',
            subprotocols=['access_token', str(AccessToken.for_user(self.customer))],
        )
        chef_socket = WebsocketCommunicator(
            websocket_application,
            f'/ws/orders/{self.order.id}/chat/',
            subprotocols=['access_token', str(AccessToken.for_user(self.chef_user))],
        )
        connected, _ = await customer_socket.connect()
        self.assertTrue(connected)
        connected, _ = await chef_socket.connect()
        self.assertTrue(connected)

        presence = await customer_socket.receive_json_from(timeout=2)
        self.assertEqual(presence['type'], 'chat.presence')
        self.assertTrue(presence['online'])

        await customer_socket.send_json_to({'action': 'typing', 'typing': True})
        typing = await chef_socket.receive_json_from(timeout=2)
        self.assertEqual(typing['type'], 'chat.typing')
        self.assertTrue(typing['typing'])

        await customer_socket.send_json_to({'action': 'send', 'message': 'ط±ط³ط§ظ„ط© ظ…ط¨ط§ط´ط±ط©'})
        events = [
            await chef_socket.receive_json_from(timeout=2),
            await chef_socket.receive_json_from(timeout=2),
        ]
        message_event = next(event for event in events if event['type'] == 'chat.message')
        self.assertEqual(message_event['data']['message'], 'ط±ط³ط§ظ„ط© ظ…ط¨ط§ط´ط±ط©')

        await customer_socket.send_json_to({
            'action': 'send',
            'message': 'ظˆط§طھط³ط§ط¨ +20 10 1234 5678',
        })
        phone_events = [
            await chef_socket.receive_json_from(timeout=2),
            await chef_socket.receive_json_from(timeout=2),
        ]
        phone_event = next(event for event in phone_events if event['type'] == 'chat.message')
        self.assertEqual(
            phone_event['data']['message'],
            'ظˆط§طھط³ط§ط¨ [طھظ… ط­ط°ظپ ط±ظ‚ظ… ط§ظ„ظ‡ط§طھظپ]',
        )

        await customer_socket.disconnect()
        await chef_socket.disconnect()

