from django.db import connection
from django.test import TestCase


class MarketplaceSchemaTests(TestCase):
    def test_required_marketplace_tables_exist(self):
        tables = set(connection.introspection.table_names())
        required = {
            'users',
            'profiles',
            'admins',
            'customers',
            'chefs',
            'governorates',
            'centers',
            'categories',
            'meals',
            'meal_images',
            'meal_videos',
            'kitchen_gallery',
            'orders',
            'order_items',
            'reviews',
            'favorites',
            'followers',
            'chats',
            'messages',
            'notifications',
            'wallets',
        }

        self.assertEqual(required - tables, set())
