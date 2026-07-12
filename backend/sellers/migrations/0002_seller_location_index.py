from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('sellers', '0001_initial')]

    operations = [
        migrations.AddIndex(
            model_name='sellerprofile',
            index=models.Index(fields=['approved', 'governorate', 'center'], name='seller_location_idx'),
        ),
    ]
