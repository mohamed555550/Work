from django.db import migrations, models
from django.utils import timezone


def populate_pickup_details(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    for order in Order.objects.select_related('seller').all().iterator():
        order.pickup_time = order.created_at or timezone.now()
        order.pickup_address = getattr(order.seller, 'pickup_address', '') or (
            f'{order.seller.center}، {order.seller.governorate}'
        )
        order.save(update_fields=['pickup_time', 'pickup_address'])


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0005_order_commission_fields'),
        ('sellers', '0011_seller_pickup_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='pickup_address',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='order',
            name='pickup_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(populate_pickup_details, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='order',
            name='pickup_address',
            field=models.CharField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='order',
            name='pickup_time',
            field=models.DateTimeField(default=timezone.now),
        ),
    ]
