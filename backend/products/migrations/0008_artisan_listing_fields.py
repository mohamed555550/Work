from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_product_available_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name='product',
            name='listing_type',
            field=models.CharField(
                choices=[('service', 'Service'), ('sale', 'For sale')],
                default='sale',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='trade',
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name='product',
            name='trade_category',
            field=models.CharField(blank=True, max_length=80),
        ),
    ]
