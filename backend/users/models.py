from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


def user_photo_upload_path(instance, filename):
    return f'users/{instance.username}/{filename}'


class UserManager(DjangoUserManager):
    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        return super()._create_user(username, self.normalize_email(email), password, **extra_fields)


class User(AbstractUser):
    ROLES = [
        ('user', 'User'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLES, default='user')
    profile_image = models.ImageField(upload_to=user_photo_upload_path, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    last_seen_at = models.DateTimeField(blank=True, null=True)
    objects = UserManager()

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['role', 'is_active'], name='users_role_active_idx'),
            models.Index(fields=['date_joined'], name='users_joined_idx'),
        ]

    def is_seller(self):
        return self.role == 'seller'


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=32, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to=user_photo_upload_path, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profiles'


class Admin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_profile')
    permissions = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admins'


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_profile')
    default_address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(max_length=3, default='EGP')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wallets'
        constraints = [
            models.CheckConstraint(condition=models.Q(balance__gte=0), name='wallet_balance_nonnegative'),
        ]


class Suggestion(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='suggestions',
    )
    subject = models.CharField(max_length=160)
    message = models.TextField(max_length=4000)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    email_sent_at = models.DateTimeField(blank=True, null=True)
    email_error = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'suggestions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at'], name='suggestion_status_idx'),
        ]
