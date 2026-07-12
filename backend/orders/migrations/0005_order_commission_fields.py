from decimal import Decimal, ROUND_HALF_UP

from django.db import migrations, models


def backfill_order_financials(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    for order in Order.objects.all().iterator():
        fee = (
            order.total_price * Decimal('0.10')
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        Order.objects.filter(pk=order.pk).update(
            commission_rate=Decimal('10.00'),
            platform_fee=fee,
            seller_earnings=order.total_price - fee,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0004_orderitem_order_item_quantity_positive_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='commission_rate',
            field=models.DecimalField(decimal_places=2, default=Decimal('10.00'), max_digits=5),
        ),
        migrations.AddField(
            model_name='order',
            name='platform_fee',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='order',
            name='seller_earnings',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.RunPython(backfill_order_financials, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='order',
            constraint=models.CheckConstraint(
                condition=models.Q(platform_fee__gte=0),
                name='order_platform_fee_nonnegative',
            ),
        ),
        migrations.AddConstraint(
            model_name='order',
            constraint=models.CheckConstraint(
                condition=models.Q(seller_earnings__gte=0),
                name='order_seller_earnings_nonnegative',
            ),
        ),
    ]
