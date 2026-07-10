from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.cache import cache
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase
from sellers.models import Center, Governorate, SellerProfile
from users.models import Suggestion, User
from users.tokens import email_verification_token


class AuthenticationTests(APITestCase):
    def setUp(self):
        cache.clear()

    def test_register_sends_verification_and_verification_returns_tokens(self):
        response = self.client.post(reverse('register'), {
            'username': 'new_user',
            'email': 'new@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'first_name': 'New',
            'last_name': 'User',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.data['data']
        self.assertEqual(payload['user']['username'], 'new_user')
        self.assertFalse(payload['user']['email_verified'])
        self.assertEqual(len(mail.outbox), 1)

        user = User.objects.get(username='new_user')
        verification_payload = {
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': email_verification_token.make_token(user),
        }
        verification = self.client.post(reverse('verify_email'), verification_payload)
        self.assertEqual(verification.status_code, status.HTTP_200_OK)
        self.assertIn('access', verification.data['data'])
        user.refresh_from_db()
        self.assertTrue(user.email_verified)
        replay = self.client.post(reverse('verify_email'), verification_payload)
        self.assertEqual(replay.status_code, status.HTTP_400_BAD_REQUEST, replay.data)

    def test_register_rejects_mismatched_passwords(self):
        response = self.client.post(reverse('register'), {
            'username': 'new_user',
            'password': 'StrongPassword123!',
            'password_confirm': 'DifferentPassword123!',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_chef_registration_activates_profile_without_storing_plain_national_id(self):
        governorate = Governorate.objects.get(name_ar='الدقهلية')
        Center.objects.get(governorate=governorate, name_ar='المنصورة')

        response = self.client.post(reverse('register_chef'), {
            'username': 'new-chef',
            'email': 'new-chef@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'first_name': 'منى',
            'last_name': 'محمد',
            'kitchen_name': 'مطبخ منى',
            'governorate': 'الدقهلية',
            'center': 'المنصورة',
            'age': 32,
            'national_id': '29801011234567',
            'food_description': 'أكلات مصرية منزلية',
            'pickup_address': 'شارع الجمهورية، المنصورة، الدقهلية',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        user = User.objects.get(username='new-chef')
        profile = SellerProfile.objects.get(user=user)
        self.assertEqual(user.role, 'seller')
        self.assertEqual(profile.approved, 'approved')
        self.assertEqual(profile.age, 32)
        self.assertEqual(profile.national_id_last4, '4567')
        self.assertNotEqual(profile.national_id_hash, '29801011234567')
        self.assertEqual(profile.center_record.name_ar, 'المنصورة')

    def test_login_requires_verified_email(self):
        user = User.objects.create_user(
            username='login-user',
            email='login@example.com',
            password='Password123!',
            email_verified=False,
        )
        blocked = self.client.post(reverse('token_obtain_pair'), {
            'username': user.username,
            'password': 'Password123!',
        })
        self.assertEqual(blocked.status_code, status.HTTP_400_BAD_REQUEST)

        user.email_verified = True
        user.save(update_fields=['email_verified'])
        allowed = self.client.post(reverse('token_obtain_pair'), {
            'username': user.username,
            'password': 'Password123!',
        })
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)
        self.assertEqual(allowed.data['user']['email'], user.email)

    def test_register_rejects_duplicate_email_case_insensitively(self):
        User.objects.create_user(username='existing', email='taken@example.com', password='Password123!')
        response = self.client.post(reverse('register'), {
            'username': 'new_user',
            'email': 'TAKEN@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_changes_password_without_disclosing_email(self):
        user = User.objects.create_user(username='reset-user', email='reset@example.com', password='OldPassword123!')
        response = self.client.post(reverse('forgot_password'), {'email': user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

        confirm = self.client.post(reverse('reset_password'), {
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            'password': 'NewPassword123!',
            'password_confirm': 'NewPassword123!',
        })
        self.assertEqual(confirm.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password('NewPassword123!'))

    def test_logout_blacklists_refresh_token(self):
        user = User.objects.create_user(
            username='logout-user',
            email='logout@example.com',
            password='Password123!',
            email_verified=True,
        )
        login = self.client.post(reverse('token_obtain_pair'), {
            'username': user.username,
            'password': 'Password123!',
        })
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        logout = self.client.post(reverse('logout'), {'refresh': login.data['refresh']})
        self.assertEqual(logout.status_code, status.HTTP_200_OK)
        self.client.credentials()
        refresh = self.client.post(reverse('token_refresh'), {'refresh': login.data['refresh']})
        self.assertEqual(refresh.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_suggestion_is_stored_and_emailed_to_owner(self):
        user = User.objects.create_user(
            username='suggestion-user',
            email='suggestion-user@example.com',
            password='Password123!',
        )
        self.client.force_authenticate(user)

        response = self.client.post(reverse('suggestion_create'), {
            'subject': 'اقتراح جديد',
            'message': 'أتمنى إضافة خيارات جديدة للوجبات الصحية.',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        suggestion = Suggestion.objects.get(user=user)
        self.assertEqual(suggestion.status, 'sent')
        self.assertEqual(mail.outbox[-1].to, ['elnono55555@gmail.com'])
        self.assertIn(user.email, mail.outbox[-1].body)
