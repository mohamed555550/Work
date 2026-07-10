from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('products', '0002_product_is_available')]

    operations = [
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['is_available', 'category', 'price'], name='product_catalog_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['seller', 'is_available'], name='product_seller_idx'),
        ),
    ]
