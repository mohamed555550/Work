from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0007_alter_order_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160)),
                ('description', models.TextField(max_length=2000)),
                ('governorate', models.CharField(max_length=120)),
                ('center', models.CharField(max_length=120)),
                ('trade', models.CharField(blank=True, default='', max_length=80)),
                ('trade_category', models.CharField(blank=True, default='', max_length=80)),
                ('status', models.CharField(choices=[('open', 'Open'), ('in_progress', 'In progress'), ('closed', 'Closed')], default='open', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'service_requests',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['status', 'governorate', 'center', '-created_at'], name='service_req_location_idx'),
                    models.Index(fields=['customer', 'status', '-created_at'], name='service_req_customer_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='ServiceRequestImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='service-requests/images/')),
                ('sort_order', models.PositiveSmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='orders.servicerequest')),
            ],
            options={
                'db_table': 'service_request_images',
                'ordering': ['sort_order', 'id'],
                'indexes': [
                    models.Index(fields=['request', 'sort_order'], name='service_req_image_sort_idx'),
                ],
            },
        ),
        migrations.AddField(
            model_name='order',
            name='service_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='orders.servicerequest'),
        ),
    ]
