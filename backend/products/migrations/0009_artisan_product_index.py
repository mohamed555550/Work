from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_artisan_listing_fields'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='product',
            name='product_catalog_idx',
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['is_available', 'trade', 'price'], name='product_catalog_idx'),
        ),
    ]
