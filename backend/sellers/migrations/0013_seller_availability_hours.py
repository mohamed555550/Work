from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sellers', '0012_seller_professions'),
    ]

    operations = [
        migrations.AddField(
            model_name='sellerprofile',
            name='is_open',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='sellerprofile',
            name='work_start_time',
            field=models.TimeField(default='09:00'),
        ),
        migrations.AddField(
            model_name='sellerprofile',
            name='work_end_time',
            field=models.TimeField(default='17:00'),
        ),
    ]
