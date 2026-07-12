from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('orders', '0002_remove_delivery')]

    operations = [
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['user', 'status', '-created_at'], name='order_customer_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['seller', 'status', '-created_at'], name='order_seller_idx'),
        ),
    ]
