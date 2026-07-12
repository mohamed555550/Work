from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
import io
import tempfile
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from .models import Center, Follower, Governorate, SellerProfile
from favorites.models import Favorite


class PublicSellerApiTests(APITestCase):
    def setUp(self):
        owner = User.objects.create_user(
            username='chef',
            email='private-chef@example.com',
            password='Password123!',
            role='seller',
            email_verified=True,
        )
        self.profile = SellerProfile.objects.create(
            user=owner,
            name='مطبخ آمن',
            governorate='المنيا',
            center='مركز المنيا',
            food_description='وجبات منزلية',
            approved='approved',
        )

    def test_public_seller_response_never_exposes_contact_details(self):
        response = self.client.get(reverse('seller_public_detail', args=[self.profile.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('email', response.data)
        self.assertNotIn('username', response.data)
        self.assertNotIn('phone', response.data)

    def test_public_list_filters_by_location(self):
        response = self.client.get(reverse('seller_public_list'), {
            'governorate': 'المنيا',
            'center': 'مركز المنيا',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_locations_are_served_from_database(self):
        governorate = Governorate.objects.create(
            icon='📍',
            name_ar='محافظة اختبار',
            name_en='Test Governorate',
            slug='test-governorate',
        )
        Center.objects.create(
            governorate=governorate,
            name_ar='مركز اختبار',
            name_en='Test Center',
            slug='test-center',
        )

        response = self.client.get(reverse('governorate_list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = next(item for item in response.data if item['slug'] == 'test-governorate')
        self.assertEqual(result['icon'], '📍')
        self.assertEqual(result['centers'][0]['name'], 'مركز اختبار')

    def test_customer_can_follow_and_favorite_chef_idempotently(self):
        customer = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='Password123!',
            email_verified=True,
        )
        self.client.force_authenticate(customer)

        for _ in range(2):
            self.assertEqual(
                self.client.post(reverse('seller_follow', args=[self.profile.id])).status_code,
                status.HTTP_200_OK,
            )
            self.assertEqual(
                self.client.post(reverse('seller_favorite', args=[self.profile.id])).status_code,
                status.HTTP_200_OK,
            )

        self.assertEqual(Follower.objects.filter(customer=customer, chef=self.profile).count(), 1)
        self.assertEqual(Favorite.objects.filter(user=customer, chef=self.profile).count(), 1)

    def test_customer_can_activate_chef_account_without_manual_review(self):
        customer = User.objects.create_user(
            username='future-chef',
            email='future-chef@example.com',
            password='Password123!',
            email_verified=True,
        )
        self.client.force_authenticate(customer)
        response = self.client.post(reverse('seller_apply'), {
            'name': 'مطبخ المستقبل',
            'governorate': 'القاهرة',
            'center': 'مدينة نصر',
            'food_description': 'وجبات منزلية طازجة',
            'pickup_address': 'شارع عباس العقاد، مدينة نصر، القاهرة',
            'age': 30,
            'national_id': '29501011234567',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        customer.refresh_from_db()
        self.assertEqual(customer.role, 'seller')
        self.assertEqual(customer.seller_profile.approved, 'approved')
        self.assertEqual(
            customer.seller_profile.pickup_address,
            'شارع عباس العقاد، مدينة نصر، القاهرة',
        )

    def test_seeded_locations_include_all_governorates_and_complete_centers(self):
        self.assertEqual(Governorate.objects.count(), 27)
        self.assertGreaterEqual(Center.objects.count(), 279)
        expected = {
            'البحيرة': {'أبو المطامير', 'المحمودية', 'شبراخيت'},
            'الدقهلية': {'أجا', 'منية النصر', 'نبروه'},
            'الشرقية': {'مشتول السوق', 'ههيا', 'أولاد صقر'},
            'أسيوط': {'الغنايم', 'ساحل سليم', 'الفتح'},
            'سوهاج': {'المنشأة', 'جهينة', 'العسيرات'},
            'القاهرة': {'السيدة زينب', 'مصر القديمة', '15 مايو'},
            'جنوب سيناء': {'طابا', 'أبو رديس', 'أبو زنيمة'},
        }
        for governorate_name, center_names in expected.items():
            actual = set(
                Center.objects.filter(governorate__name_ar=governorate_name)
                .values_list('name_ar', flat=True)
            )
            self.assertTrue(center_names.issubset(actual))

    def test_governorates_are_ordered_by_population_descending(self):
        response = self.client.get(reverse('governorate_list'))
        names = [item['name'] for item in response.data]
        populations = [item['estimated_population'] for item in response.data]

        self.assertEqual(names[:5], [
            'القاهرة', 'الجيزة', 'الشرقية', 'الدقهلية', 'البحيرة',
        ])
        self.assertEqual(names[-1], 'جنوب سيناء')
        self.assertEqual(populations, sorted(populations, reverse=True))
        self.assertTrue(all(value > 0 for value in populations))

    def test_chef_can_update_cover_and_profile_images(self):
        def upload(name, color):
            output = io.BytesIO()
            Image.new('RGB', (120, 80), color).save(output, format='PNG')
            return SimpleUploadedFile(name, output.getvalue(), content_type='image/png')

        self.client.force_authenticate(self.profile.user)
        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            response = self.client.patch(
                reverse('seller_profile'),
                {
                    'cover_image': upload('cover.png', '#222222'),
                    'profile_image': upload('profile.png', '#ff6600'),
                },
                format='multipart',
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.profile.refresh_from_db()
            self.profile.user.refresh_from_db()
            self.assertTrue(self.profile.cover_image.name.endswith('.webp'))
            self.assertTrue(self.profile.user.profile_image.name.endswith('.webp'))
