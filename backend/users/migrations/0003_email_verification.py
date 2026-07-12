from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_alter_user_groups_alter_user_is_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='email_verified',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
    ]
