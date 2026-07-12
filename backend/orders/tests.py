from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from notifications.models import Notification
from products.models import Product
from sellers.models import SellerProfile
from users.models import User


class OrderApiTests(APITestCase):
    def setUp(self):
        seller_user = User.objects.create_user(username='seller', email='seller@example.com', password='Password123!', role='seller')
        self.seller = SellerProfile.objects.create(
            user=seller_user,
            name='Test Kitchen',
            governorate='Cairo',
            center='Nasr City',
            food_description='Test food',
            pickup_address='شارع الاختبار، مدينة نصر، القاهرة',
            approved='approved',
        )
        self.product = Product.objects.create(
            seller=self.seller,
            name='Meal',
            price='50.00',
            category='lunch',
            preparation_time=20,
        )
        self.user = User.objects.create_user(username='buyer', email='buyer@example.com', password='Password123!')
        self.client.force_authenticate(self.user)

    def order_payload(self, key='same-key'):
        return {
            'idempotency_key': key,
            'pickup_time': (timezone.now() + timedelta(hours=1)).isoformat(),
            'items': [{'product': self.product.id, 'quantity': 2}],
        }

    def test_order_is_pickup_only_and_has_no_delivery_field(self):
        response = self.client.post(reverse('order_create'), self.order_payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('delivery_type', response.data['data'])
        self.assertEqual(response.data['data']['total_price'], '100.00')
        self.assertEqual(response.data['data']['commission_rate'], '10.00')
        self.assertEqual(response.data['data']['platform_fee'], '10.00')
        self.assertEqual(response.data['data']['seller_earnings'], '90.00')
        self.assertEqual(response.data['data']['pickup_address'], self.seller.pickup_address)
        chef_notification = Notification.objects.get(
            user=self.seller.user,
            order_id=response.data['data']['id'],
        )
        self.assertEqual(chef_notification.title, 'طلب جديد')
        self.assertIn(self.user.username, chef_notification.content)

    def test_delivery_field_is_rejected(self):
        payload = {**self.order_payload(), 'delivery_type': 'chef_delivery'}
        response = self.client.post(reverse('order_create'), payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_same_idempotency_key_returns_same_order(self):
        first = self.client.post(reverse('order_create'), self.order_payload(), format='json')
        second = self.client.post(reverse('order_create'), self.order_payload(), format='json')

        self.assertEqual(first.data['data']['id'], second.data['data']['id'])
