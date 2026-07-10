from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone


class Category(models.Model):
    name_ar = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'categories'
        ordering = ['sort_order', 'name_ar']


class Product(models.Model):
    seller = models.ForeignKey('sellers.SellerProfile', on_delete=models.CASCADE, related_name='products')
    LISTING_CHOICES = [
        ('service', 'Service'),
        ('sale', 'For sale'),
    ]
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    ingredients = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.CharField(max_length=80, blank=True)
    listing_type = models.CharField(max_length=20, choices=LISTING_CHOICES, default='sale')
    trade = models.CharField(max_length=80, blank=True)
    trade_category = models.CharField(max_length=80, blank=True)
    category_record = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.PROTECT, related_name='meals'
    )
    preparation_time = models.PositiveIntegerField(help_text='Minutes')
    is_available = models.BooleanField(default=True)
    available_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'meals'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_available', 'trade', 'price'], name='product_catalog_idx'),
            models.Index(fields=['seller', 'is_available'], name='product_seller_idx'),
        ]

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        ratings = self.reviews.all().values_list('rating', flat=True)
        return round(sum(ratings) / len(ratings), 1) if ratings else 0

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def can_order(self):
        return self.is_available or bool(
            self.available_at and self.available_at <= timezone.now()
        )


class Meal(Product):
    """Canonical domain name; Product remains for API compatibility."""

    class Meta:
        proxy = True


class MealImage(models.Model):
    meal = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='meals/images/')
    alt_text = models.CharField(max_length=240, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'meal_images'
        ordering = ['sort_order', 'id']
        indexes = [
            models.Index(fields=['meal', 'sort_order'], name='meal_image_sort_idx'),
        ]


class MealVideo(models.Model):
    meal = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='meals/videos/', blank=True)
    external_url = models.URLField(max_length=500, blank=True)
    thumbnail = models.ImageField(upload_to='meals/video-thumbnails/', blank=True, null=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'meal_videos'
        ordering = ['sort_order', 'id']
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(video='') | ~models.Q(external_url=''),
                name='meal_video_has_source',
            ),
        ]


class SearchHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_history',
    )
    query = models.CharField(max_length=500)
    normalized_query = models.CharField(max_length=500)
    governorate = models.CharField(max_length=120, blank=True)
    center = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'search_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at'], name='search_user_time_idx'),
        ]
