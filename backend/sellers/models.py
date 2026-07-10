from django.db import models
from django.conf import settings


class Governorate(models.Model):
    icon = models.CharField(max_length=16, default='📍')
    name_ar = models.CharField(max_length=120, unique=True)
    name_en = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    is_active = models.BooleanField(default=True)
    estimated_population = models.PositiveBigIntegerField(default=0)
    population_as_of = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'governorates'
        ordering = ['-estimated_population', 'name_ar']

    def __str__(self):
        return self.name_ar


class Center(models.Model):
    governorate = models.ForeignKey(Governorate, on_delete=models.PROTECT, related_name='centers')
    name_ar = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'centers'
        ordering = ['name_ar']
        constraints = [
            models.UniqueConstraint(fields=['governorate', 'slug'], name='center_governorate_slug_uniq'),
        ]
        indexes = [
            models.Index(fields=['governorate', 'is_active'], name='center_gov_active_idx'),
        ]

    def __str__(self):
        return self.name_ar


class SellerProfile(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_profile')
    name = models.CharField(max_length=180)
    governorate = models.CharField(max_length=120)
    center = models.CharField(max_length=120)
    governorate_record = models.ForeignKey(
        Governorate, null=True, blank=True, on_delete=models.PROTECT, related_name='chefs'
    )
    center_record = models.ForeignKey(
        Center, null=True, blank=True, on_delete=models.PROTECT, related_name='chefs'
    )
    food_description = models.TextField()
    professions = models.JSONField(default=list, blank=True)
    pickup_address = models.CharField(max_length=500, blank=True)
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    national_id_hash = models.CharField(max_length=64, blank=True, null=True, unique=True)
    national_id_last4 = models.CharField(max_length=4, blank=True)
    cover_image = models.ImageField(upload_to='kitchens/covers/', blank=True, null=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    is_open = models.BooleanField(default=True)
    work_start_time = models.TimeField(default='09:00')
    work_end_time = models.TimeField(default='17:00')
    is_online = models.BooleanField(default=False)
    last_seen_at = models.DateTimeField(blank=True, null=True)
    approved = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chefs'
        indexes = [
            models.Index(fields=['approved', 'governorate', 'center'], name='seller_location_idx'),
            models.Index(fields=['approved', 'governorate_record', 'center_record'], name='chef_location_idx'),
        ]

    @property
    def is_active_seller(self):
        return self.approved == 'approved'

    def __str__(self):
        return f'{self.name} ({self.user.username})'


class Chef(SellerProfile):
    """Canonical domain name; SellerProfile remains for API compatibility."""

    class Meta:
        proxy = True


class KitchenGallery(models.Model):
    chef = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='kitchen_gallery')
    image = models.ImageField(upload_to='kitchens/gallery/')
    caption = models.CharField(max_length=240, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'kitchen_gallery'
        ordering = ['sort_order', 'id']
        indexes = [
            models.Index(fields=['chef', 'sort_order'], name='kitchen_chef_sort_idx'),
        ]


class Follower(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chef_follows'
    )
    chef = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'followers'
        constraints = [
            models.UniqueConstraint(fields=['customer', 'chef'], name='follower_customer_chef_uniq'),
        ]
        indexes = [
            models.Index(fields=['chef', '-created_at'], name='followers_chef_time_idx'),
        ]
