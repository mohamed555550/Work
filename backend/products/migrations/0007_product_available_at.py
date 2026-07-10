from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0006_product_ingredients'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='available_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
