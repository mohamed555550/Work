from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('chat', '0001_initial')]

    operations = [
        migrations.AddIndex(
            model_name='chatmessage',
            index=models.Index(fields=['order', 'created_at'], name='chat_order_time_idx'),
        ),
    ]
