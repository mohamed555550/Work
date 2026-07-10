from decimal import Decimal
from datetime import time

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Product
from sellers.models import Center, SellerProfile
from users.models import User


class Command(BaseCommand):
    help = 'Seed Sanay3y workers and listings, including one worker for every active center.'

    WORKERS = [
        ('نجار أبواب وشبابيك', 'carpenter', 'doors', 'نجارة أبواب وشبابيك وأثاث حسب المقاس.'),
        ('كهربائي تشطيب وصيانة', 'electrician', 'wiring', 'تشطيب وصيانة كهرباء للمنازل والمحلات.'),
        ('سباك تركيب وصيانة', 'plumber', 'pipes', 'تركيب وصيانة مواسير وخلاطات وسخانات.'),
        ('نقاش ودهانات', 'painter', 'walls', 'دهانات داخلية وخارجية وتشطيبات نظيفة.'),
        ('فني ألوميتال', 'aluminum', 'windows', 'شبابيك وأبواب ألوميتال وصيانة قطاعات.'),
        ('فني تكييف', 'ac-technician', 'split', 'تركيب وصيانة تكييفات وتنظيف وحدات.'),
        ('ميكانيكي سيارات', 'car-mechanic', 'engine', 'كشف وصيانة أعطال السيارات.'),
        ('فني أجهزة منزلية', 'appliance-repair', 'washing-machines', 'صيانة غسالات وثلاجات وأجهزة منزلية.'),
    ]

    PRODUCTS = [
        ('باب خشب جاهز', 'باب خشب قابل للتعديل حسب المقاس.', '3200.00', 'sale', 'carpenter', 'doors', 120),
        ('لوحة توزيع كهرباء', 'لوحة توزيع مناسبة للشقق والمحلات.', '950.00', 'sale', 'electrician', 'wiring', 60),
        ('طقم خلاط حمام', 'خلاط حمام جديد مع إمكانية التركيب.', '700.00', 'sale', 'plumber', 'fixtures', 45),
        ('دهان غرفة', 'خدمة دهان غرفة متوسطة بالخامات حسب الاتفاق.', '0.00', 'service', 'painter', 'walls', 180),
        ('شباك ألوميتال', 'شباك ألوميتال جاهز ومتاح بمقاسات مختلفة.', '1800.00', 'sale', 'aluminum', 'windows', 120),
        ('صيانة تكييف', 'زيارة صيانة وتنظيف وحدة تكييف.', '0.00', 'service', 'ac-technician', 'maintenance', 90),
        ('كشف أعطال سيارة', 'كشف مبدئي على أعطال السيارة.', '0.00', 'service', 'car-mechanic', 'engine', 60),
        ('صيانة غسالة', 'صيانة غسالة أوتوماتيك حسب العطل.', '0.00', 'service', 'appliance-repair', 'washing-machines', 80),
    ]

    @transaction.atomic
    def handle(self, *args, **options):
        self.default_password = make_password('Password123!')
        self.seed_users()
        launch_workers = self.seed_launch_workers()
        self.seed_products(launch_workers)
        center_workers, center_products = self.seed_every_center()
        self.stdout.write(self.style.SUCCESS(
            f'Seed complete: {len(launch_workers)} launch workers, '
            f'{center_workers} center workers, and {center_products} center listings.'
        ))

    def seed_users(self):
        for username, email, first_name in [
            ('mohamed', 'mohamed@example.com', 'محمد'),
            ('alaa', 'alaa@example.com', 'آلاء'),
            ('salma', 'salma@example.com', 'سلمى'),
        ]:
            user, created = User.objects.get_or_create(username=username, defaults={
                'email': email,
                'first_name': first_name,
                'role': 'user',
                'email_verified': True,
            })
            if created:
                user.password = self.default_password
            user.email_verified = True
            user.save()

    def upsert_worker(self, username, name, governorate, center, trade, category, description, center_record=None):
        user, created = User.objects.get_or_create(username=username, defaults={
            'email': f'{username}@example.com',
            'first_name': name,
            'role': 'seller',
            'email_verified': True,
        })
        if created:
            user.password = self.default_password
        user.email = f'{username}@example.com'
        user.first_name = name
        user.role = 'seller'
        user.email_verified = True
        user.save()
        profile, _ = SellerProfile.objects.update_or_create(user=user, defaults={
            'name': name,
            'governorate': governorate,
            'center': center,
            'governorate_record': center_record.governorate if center_record else None,
            'center_record': center_record,
            'food_description': description,
            'pickup_address': f'{center}، {governorate}',
            'experience_years': 3 + (user.id % 12),
            'is_open': True,
            'work_start_time': time(9, 0),
            'work_end_time': time(18, 0),
            'professions': [{'trade': trade, 'category': category}],
            'approved': 'approved',
        })
        return profile

    def seed_launch_workers(self):
        workers = []
        for index, (name, trade, category, description) in enumerate(self.WORKERS, start=1):
            workers.append(self.upsert_worker(
                f'worker{index}',
                name,
                'المنيا',
                'مركز المنيا',
                trade,
                category,
                description,
            ))
        return workers

    def seed_products(self, sellers):
        for index, (name, description, price, listing_type, trade, category, prep) in enumerate(self.PRODUCTS):
            seller = sellers[index % len(sellers)]
            Product.objects.update_or_create(
                name=name,
                seller=seller,
                defaults={
                    'description': description,
                    'ingredients': description,
                    'price': Decimal(price),
                    'category': category,
                    'listing_type': listing_type,
                    'trade': trade,
                    'trade_category': category,
                    'preparation_time': prep,
                    'is_available': True,
                },
            )

    def seed_every_center(self):
        centers = Center.objects.filter(
            is_active=True,
            governorate__is_active=True,
        ).select_related('governorate').order_by('governorate_id', 'id')
        seller_count = 0
        product_count = 0

        for center in centers:
            worker_name, trade, category, description = self.WORKERS[(center.id - 1) % len(self.WORKERS)]
            profile = self.upsert_worker(
                f'sanay3y_center_worker_{center.id}',
                f'{worker_name} - {center.name_ar}',
                center.governorate.name_ar,
                center.name_ar,
                trade,
                category,
                f'{description} متاح داخل {center.name_ar}.',
                center,
            )
            seller_count += 1

            name, product_description, price, listing_type, _, _, prep = self.PRODUCTS[
                (center.id - 1) % len(self.PRODUCTS)
            ]
            Product.objects.update_or_create(
                seller=profile,
                name=name,
                defaults={
                    'description': f'{product_description} متاح داخل {center.name_ar}.',
                    'ingredients': product_description,
                    'price': Decimal(price),
                    'category': category,
                    'listing_type': listing_type,
                    'trade': trade,
                    'trade_category': category,
                    'preparation_time': prep,
                    'is_available': True,
                },
            )
            product_count += 1

        return seller_count, product_count
