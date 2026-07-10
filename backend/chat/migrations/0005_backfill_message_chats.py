import django.db.models.deletion
from django.db import migrations, models


def backfill_message_chats(apps, schema_editor):
    Chat = apps.get_model('chat', 'Chat')
    Message = apps.get_model('chat', 'ChatMessage')
    Order = apps.get_model('orders', 'Order')

    order_ids = Message.objects.filter(chat__isnull=True).values_list(
        'order_id', flat=True
    ).distinct()
    for order in Order.objects.filter(id__in=order_ids).iterator():
        chat, _ = Chat.objects.get_or_create(
            order_id=order.id,
            defaults={
                'customer_id': order.user_id,
                'chef_id': order.seller_id,
            },
        )
        Message.objects.filter(order_id=order.id, chat__isnull=True).update(chat_id=chat.id)


class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0004_chatmessage_deleted_for_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_message_chats, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='chatmessage',
            name='chat',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='messages',
                to='chat.chat',
            ),
        ),
    ]
