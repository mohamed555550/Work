from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sellers', '0008_governorate_population'),
    ]

    operations = [
        migrations.AddField(
            model_name='sellerprofile',
            name='age',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sellerprofile',
            name='national_id_hash',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='sellerprofile',
            name='national_id_last4',
            field=models.CharField(blank=True, max_length=4),
        ),
    ]
