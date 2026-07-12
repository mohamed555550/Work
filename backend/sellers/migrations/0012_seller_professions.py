from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sellers', '0011_seller_pickup_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='sellerprofile',
            name='professions',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
