from django.db import migrations, models


def convert_delivery_orders_to_pickup(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    Order.objects.filter(status='out_for_delivery').update(status='ready_for_pickup')


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(convert_delivery_orders_to_pickup, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='order',
            name='delivery_type',
        ),
        migrations.AlterField(
            model_name='order',
            name='idempotency_key',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'قيد الانتظار'),
                    ('confirmed_by_seller', 'تم التأكيد من الشيف'),
                    ('preparing', 'قيد التحضير'),
                    ('ready_for_pickup', 'جاهز للاستلام'),
                    ('completed', 'مكتمل'),
                    ('canceled', 'ملغي'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
        migrations.AddConstraint(
            model_name='order',
            constraint=models.UniqueConstraint(
                fields=('user', 'idempotency_key'),
                name='unique_order_key_per_user',
            ),
        ),
    ]
