import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_backfill_message_chats'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportConversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed')], default='open', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='support_conversation', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'support_conversations',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='SupportMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(max_length=4000)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.supportconversation')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_support_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'support_messages',
                'ordering': ['created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='supportconversation',
            index=models.Index(fields=['status', '-updated_at'], name='support_status_time_idx'),
        ),
        migrations.AddIndex(
            model_name='supportmessage',
            index=models.Index(fields=['conversation', 'created_at'], name='support_message_time_idx'),
        ),
        migrations.AddIndex(
            model_name='supportmessage',
            index=models.Index(fields=['conversation', 'read_at'], name='support_message_read_idx'),
        ),
    ]
