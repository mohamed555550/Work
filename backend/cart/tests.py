from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from products.models import Product
from sellers.models import SellerProfile
from users.models import User


class CartApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='buyer', email='buyer@example.com', password='Password123!')
        self.client.force_authenticate(self.user)
        self.products = []
        for index in range(2):
            seller_user = User.objects.create_user(username=f'seller{index}', email=f'seller{index}@example.com', password='Password123!', role='seller')
            seller = SellerProfile.objects.create(
                user=seller_user,
                name=f'Kitchen {index}',
                governorate='Cairo',
                center='Center',
                food_description='Food',
                approved='approved',
            )
            self.products.append(Product.objects.create(
                seller=seller,
                name=f'Meal {index}',
                price='50.00',
                category='lunch',
                preparation_time=20,
            ))

    def test_empty_cart_is_returned_as_a_list(self):
        response = self.client.get(reverse('cart_list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'], [])

    def test_cart_rejects_products_from_multiple_sellers(self):
        first = self.client.post(reverse('cart_add'), {
            'product': self.products[0].id,
            'quantity': 1,
        }, format='json')
        second = self.client.post(reverse('cart_add'), {
            'product': self.products[1].id,
            'quantity': 1,
        }, format='json')

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
