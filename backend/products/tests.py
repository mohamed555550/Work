import io
import tempfile
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from favorites.models import Favorite
from orders.models import Order, OrderItem
from reviews.models import Review
from sellers.models import Center, Governorate, SellerProfile
from users.models import User
from .models import Product, SearchHistory


class IntelligentMarketplaceTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='recommend-user',
            email='recommend@example.com',
            password='Password123!',
            email_verified=True,
        )
        mansoura_user = User.objects.create_user(
            username='mansoura-chef',
            email='mansoura@example.com',
            password='Password123!',
            role='seller',
        )
        cairo_user = User.objects.create_user(
            username='cairo-chef',
            email='cairo@example.com',
            password='Password123!',
            role='seller',
        )
        self.mansoura_chef = SellerProfile.objects.create(
            user=mansoura_user,
            name='شيف المنصورة',
            governorate='الدقهلية',
            center='المنصورة',
            food_description='أكل بيتي ومحاشي',
            approved='approved',
        )
        self.cairo_chef = SellerProfile.objects.create(
            user=cairo_user,
            name='ملكة الحلويات',
            governorate='القاهرة',
            center='مدينة نصر',
            food_description='حلويات وكيك',
            approved='approved',
        )
        self.mahshi = Product.objects.create(
            seller=self.mansoura_chef,
            name='محشي بيتي',
            description='محشي كرنب منزلي',
            price=120,
            category='lunch',
            preparation_time=40,
        )
        self.chicken = Product.objects.create(
            seller=self.mansoura_chef,
            name='فراخ مشوية',
            description='دجاج مشوي على الفحم',
            price=80,
            category='healthy',
            preparation_time=35,
        )
        self.dessert = Product.objects.create(
            seller=self.cairo_chef,
            name='كيك الشوكولاتة',
            description='حلوى منزلية',
            price=150,
            category='dessert',
            preparation_time=30,
        )
        Review.objects.create(user=self.user, product=self.dessert, rating=5)

    def test_natural_language_search_understands_food_location_and_intent(self):
        response = self.client.get(reverse('ai_search'), {
            'q': 'I want homemade Mahshi in Mansoura',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['meals'][0]['id'], self.mahshi.id)
        self.assertEqual(response.data['data']['interpretation']['center'], 'المنصورة')

        dessert = self.client.get(reverse('ai_search'), {'q': 'Best dessert chef'})
        self.assertEqual(dessert.data['data']['chefs'][0]['id'], self.cairo_chef.id)

        cheap = self.client.get(reverse('ai_search'), {'q': 'Cheap grilled chicken'})
        self.assertEqual(cheap.data['data']['meals'][0]['id'], self.chicken.id)

        healthy = self.client.get(reverse('ai_search'), {'q': 'Healthy breakfast'})
        self.assertEqual(healthy.data['data']['meals'][0]['id'], self.chicken.id)

    def test_recommendations_use_favorites_orders_and_persisted_searches(self):
        Favorite.objects.create(user=self.user, chef=self.mansoura_chef)
        order = Order.objects.create(
            user=self.user,
            seller=self.mansoura_chef,
            total_price=self.mahshi.price,
            status='completed',
        )
        OrderItem.objects.create(
            order=order,
            product=self.mahshi,
            quantity=1,
            unit_price=self.mahshi.price,
        )
        self.client.force_authenticate(self.user)
        self.client.get(reverse('ai_search'), {'q': 'محشي منزلي'})

        response = self.client.get(reverse('ai_recommendations'), {
            'governorate': 'الدقهلية',
            'center': 'المنصورة',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['chefs'][0]['id'], self.mansoura_chef.id)
        self.assertTrue(response.data['data']['meals'][0]['recommendation_reason'])
        self.assertEqual(SearchHistory.objects.filter(user=self.user).count(), 1)

    def test_uploaded_images_are_resized_and_converted_to_webp(self):
        source = io.BytesIO()
        Image.new('RGB', (3000, 20), '#ff6600').save(source, format='PNG')
        upload = SimpleUploadedFile('large.png', source.getvalue(), content_type='image/png')

        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            product = Product.objects.create(
                seller=self.mansoura_chef,
                name='صورة محسنة',
                price=90,
                category='lunch',
                preparation_time=20,
                image=upload,
            )
            self.assertTrue(product.image.name.endswith('.webp'))
            with Image.open(product.image.path) as optimized:
                self.assertLessEqual(max(optimized.size), 2048)
                self.assertEqual(optimized.format, 'WEBP')


class ChefMealManagementTests(APITestCase):
    def setUp(self):
        governorate = Governorate.objects.get(name_ar='القاهرة')
        Center.objects.get(governorate=governorate, name_ar='مدينة نصر')

    def test_chef_can_publish_and_schedule_meal_without_losing_it(self):
        registration = self.client.post(reverse('register_chef'), {
            'username': 'new-chef',
            'email': 'new-chef@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'first_name': 'شيف',
            'last_name': 'جديد',
            'kitchen_name': 'مطبخ البيت',
            'governorate': 'القاهرة',
            'center': 'مدينة نصر',
            'age': 32,
            'national_id': '29001011234567',
            'food_description': 'أكل بيتي طازج',
            'pickup_address': 'شارع عباس العقاد، مدينة نصر، القاهرة',
        })
        self.assertEqual(registration.status_code, status.HTTP_200_OK, registration.data)

        chef = User.objects.get(username='new-chef')
        self.assertEqual(chef.role, 'seller')
        self.assertEqual(chef.seller_profile.age, 32)
        self.assertEqual(chef.seller_profile.national_id_last4, '4567')
        self.assertNotIn('29001011234567', chef.seller_profile.national_id_hash)
        self.assertEqual(chef.seller_profile.approved, 'approved')
        self.client.force_authenticate(chef)

        created = self.client.post(reverse('product_create'), {
            'name': 'محشي ورق عنب',
            'description': 'وجبة بيتية',
            'ingredients': 'ورق عنب، أرز، صلصة، توابل',
            'price': '140.00',
            'category': 'lunch',
            'preparation_time': 45,
            'is_available': True,
        })
        self.assertEqual(created.status_code, status.HTTP_200_OK, created.data)
        meal_id = created.data['data']['id']

        public_before = self.client.get(reverse('product_list'))
        self.assertEqual(
            [meal['id'] for meal in public_before.data['data']],
            [meal_id],
        )

        available_at = timezone.now() + timedelta(days=1)
        scheduled = self.client.patch(
            reverse('product_manage', kwargs={'pk': meal_id}),
            {
                'is_available': False,
                'available_at': available_at.isoformat(),
            },
            format='json',
        )
        self.assertEqual(scheduled.status_code, status.HTTP_200_OK, scheduled.data)
        self.assertFalse(scheduled.data['data']['is_available'])

        public_after = self.client.get(reverse('product_list'))
        self.assertEqual(len(public_after.data['data']), 1)
        self.assertFalse(public_after.data['data'][0]['can_order'])
        self.assertIsNotNone(public_after.data['data'][0]['available_at'])

        seller_meals = self.client.get(reverse('seller_product_list'))
        self.assertEqual(len(seller_meals.data['data']), 1)
        self.assertEqual(seller_meals.data['data'][0]['id'], meal_id)
        self.assertFalse(seller_meals.data['data'][0]['is_available'])

        Product.objects.filter(pk=meal_id).update(
            available_at=timezone.now() - timedelta(minutes=1),
        )
        available_again = self.client.get(reverse('product_list'))
        self.assertTrue(available_again.data['data'][0]['can_order'])

    def test_chef_must_set_future_date_when_scheduling_meal(self):
        user = User.objects.create_user(
            username='schedule-chef',
            email='schedule-chef@example.com',
            password='StrongPassword123!',
            role='seller',
        )
        seller = SellerProfile.objects.create(
            user=user,
            name='مطبخ المواعيد',
            governorate='القاهرة',
            center='مدينة نصر',
            food_description='أكل بالمواعيد',
            approved='approved',
        )
        meal = Product.objects.create(
            seller=seller,
            name='وجبة يومية',
            ingredients='أرز وخضار',
            price=100,
            category='lunch',
            preparation_time=30,
        )
        self.client.force_authenticate(user)

        missing_date = self.client.patch(
            reverse('product_manage', kwargs={'pk': meal.id}),
            {'is_available': False},
            format='json',
        )
        past_date = self.client.patch(
            reverse('product_manage', kwargs={'pk': meal.id}),
            {
                'is_available': False,
                'available_at': (timezone.now() - timedelta(minutes=1)).isoformat(),
            },
            format='json',
        )

        self.assertEqual(missing_date.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(past_date.status_code, status.HTTP_400_BAD_REQUEST)

    def test_meal_creation_requires_ingredients(self):
        user = User.objects.create_user(
            username='ingredient-chef',
            email='ingredient-chef@example.com',
            password='StrongPassword123!',
            role='seller',
        )
        SellerProfile.objects.create(
            user=user,
            name='مطبخ المكونات',
            governorate='القاهرة',
            center='مدينة نصر',
            food_description='أكل بيتي',
            approved='approved',
        )
        self.client.force_authenticate(user)

        response = self.client.post(reverse('product_create'), {
            'name': 'وجبة بلا مكونات',
            'price': '100.00',
            'category': 'lunch',
            'preparation_time': 30,
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ingredients', response.data['error'])
