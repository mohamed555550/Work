from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0005_searchhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='ingredients',
            field=models.TextField(blank=True),
        ),
    ]
