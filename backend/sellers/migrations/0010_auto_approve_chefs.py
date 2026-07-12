from django.db import migrations, models


def approve_pending_chefs(apps, schema_editor):
    SellerProfile = apps.get_model('sellers', 'SellerProfile')
    User = apps.get_model('users', 'User')

    pending_user_ids = list(
        SellerProfile.objects.filter(approved='pending').values_list('user_id', flat=True)
    )
    SellerProfile.objects.filter(approved='pending').update(approved='approved')
    User.objects.filter(id__in=pending_user_ids).update(role='seller')


class Migration(migrations.Migration):
    dependencies = [
        ('sellers', '0009_seller_identity_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sellerprofile',
            name='approved',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                ],
                default='approved',
                max_length=20,
            ),
        ),
        migrations.RunPython(approve_pending_chefs, migrations.RunPython.noop),
    ]
