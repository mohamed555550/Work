from django.db import migrations, models


def populate_pickup_addresses(apps, schema_editor):
    SellerProfile = apps.get_model('sellers', 'SellerProfile')
    for seller in SellerProfile.objects.filter(pickup_address='').iterator():
        seller.pickup_address = f'{seller.center}، {seller.governorate} — يُرجى تحديث العنوان بالتفصيل'
        seller.save(update_fields=['pickup_address'])


class Migration(migrations.Migration):
    dependencies = [
        ('sellers', '0010_auto_approve_chefs'),
    ]

    operations = [
        migrations.AddField(
            model_name='sellerprofile',
            name='pickup_address',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.RunPython(populate_pickup_addresses, migrations.RunPython.noop),
    ]
