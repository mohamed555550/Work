from django.db import migrations


LOCATIONS = [
    ('🏙️', 'القاهرة', 'Cairo', 'cairo', ['مدينة نصر', 'مصر الجديدة', 'المعادي', 'حلوان', 'وسط البلد', 'التجمع الخامس', 'الشروق', 'بدر']),
    ('🗿', 'الجيزة', 'Giza', 'giza', ['الدقي', 'العجوزة', 'الهرم', 'فيصل', '6 أكتوبر', 'الشيخ زايد', 'البدرشين', 'العياط']),
    ('🌊', 'الإسكندرية', 'Alexandria', 'alexandria', ['المنتزه', 'شرق', 'وسط', 'غرب', 'الجمرك', 'العجمي', 'العامرية', 'برج العرب']),
    ('🌾', 'الدقهلية', 'Dakahlia', 'dakahlia', ['المنصورة', 'طلخا', 'ميت غمر', 'دكرنس', 'بلقاس', 'السنبلاوين', 'المنزلة']),
    ('🐠', 'البحر الأحمر', 'Red Sea', 'red-sea', ['الغردقة', 'رأس غارب', 'سفاجا', 'القصير', 'مرسى علم', 'الشلاتين']),
    ('🌿', 'البحيرة', 'Beheira', 'beheira', ['دمنهور', 'كفر الدوار', 'رشيد', 'إدكو', 'أبو حمص', 'الدلنجات', 'وادي النطرون']),
    ('🏞️', 'الفيوم', 'Fayoum', 'fayoum', ['الفيوم', 'سنورس', 'إطسا', 'طامية', 'أبشواي', 'يوسف الصديق']),
    ('🌱', 'الغربية', 'Gharbia', 'gharbia', ['طنطا', 'المحلة الكبرى', 'كفر الزيات', 'زفتى', 'سمنود', 'السنطة', 'قطور']),
    ('🚢', 'الإسماعيلية', 'Ismailia', 'ismailia', ['الإسماعيلية', 'فايد', 'القنطرة شرق', 'القنطرة غرب', 'التل الكبير', 'أبو صوير']),
    ('🌳', 'المنوفية', 'Monufia', 'monufia', ['شبين الكوم', 'منوف', 'السادات', 'أشمون', 'الباجور', 'قويسنا', 'بركة السبع']),
    ('☀️', 'المنيا', 'Minya', 'minya', ['مركز المنيا', 'ملوي', 'دير مواس', 'مطاي', 'سمالوط', 'أبو قرقاص', 'بني مزار']),
    ('🌉', 'القليوبية', 'Qalyubia', 'qalyubia', ['بنها', 'شبرا الخيمة', 'قليوب', 'القناطر الخيرية', 'الخانكة', 'طوخ', 'كفر شكر']),
    ('🏜️', 'الوادي الجديد', 'New Valley', 'new-valley', ['الخارجة', 'الداخلة', 'الفرافرة', 'باريس', 'بلاط']),
    ('⚓', 'السويس', 'Suez', 'suez', ['السويس', 'الأربعين', 'عتاقة', 'الجناين', 'فيصل']),
    ('⛵', 'أسوان', 'Aswan', 'aswan', ['أسوان', 'دراو', 'كوم أمبو', 'نصر النوبة', 'إدفو']),
    ('🏺', 'أسيوط', 'Assiut', 'assiut', ['أسيوط', 'ديروط', 'القوصية', 'منفلوط', 'أبنوب', 'أبو تيج', 'صدفا']),
    ('🌴', 'بني سويف', 'Beni Suef', 'beni-suef', ['بني سويف', 'الواسطى', 'ناصر', 'إهناسيا', 'ببا', 'سمسطا', 'الفشن']),
    ('🛳️', 'بورسعيد', 'Port Said', 'port-said', ['الشرق', 'العرب', 'المناخ', 'الضواحي', 'الزهور', 'بورفؤاد']),
    ('🐟', 'دمياط', 'Damietta', 'damietta', ['دمياط', 'دمياط الجديدة', 'رأس البر', 'فارسكور', 'الزرقا', 'كفر سعد']),
    ('🌾', 'الشرقية', 'Sharqia', 'sharqia', ['الزقازيق', 'العاشر من رمضان', 'بلبيس', 'منيا القمح', 'أبو حماد', 'فاقوس', 'الحسينية']),
    ('🏖️', 'جنوب سيناء', 'South Sinai', 'south-sinai', ['الطور', 'شرم الشيخ', 'دهب', 'نويبع', 'رأس سدر', 'سانت كاترين']),
    ('🌱', 'كفر الشيخ', 'Kafr El Sheikh', 'kafr-el-sheikh', ['كفر الشيخ', 'دسوق', 'فوه', 'مطوبس', 'بلطيم', 'سيدي سالم', 'بيلا']),
    ('🏝️', 'مطروح', 'Matrouh', 'matrouh', ['مرسى مطروح', 'الحمام', 'العلمين', 'الضبعة', 'سيوة', 'السلوم']),
    ('🏛️', 'الأقصر', 'Luxor', 'luxor', ['الأقصر', 'البياضية', 'الزينية', 'القرنة', 'أرمنت', 'إسنا']),
    ('🌴', 'قنا', 'Qena', 'qena', ['قنا', 'قوص', 'نقادة', 'دشنا', 'نجع حمادي', 'فرشوط', 'أبو تشت']),
    ('⛰️', 'شمال سيناء', 'North Sinai', 'north-sinai', ['العريش', 'الشيخ زويد', 'رفح', 'بئر العبد', 'الحسنة', 'نخل']),
    ('🌅', 'سوهاج', 'Sohag', 'sohag', ['سوهاج', 'أخميم', 'المراغة', 'طهطا', 'طما', 'جرجا', 'البلينا', 'دار السلام']),
]


def seed_locations(apps, schema_editor):
    Governorate = apps.get_model('sellers', 'Governorate')
    Center = apps.get_model('sellers', 'Center')

    for icon, name_ar, name_en, slug, centers in LOCATIONS:
        governorate, _ = Governorate.objects.update_or_create(
            slug=slug,
            defaults={
                'icon': icon,
                'name_ar': name_ar,
                'name_en': name_en,
                'is_active': True,
            },
        )
        for position, center_name in enumerate(centers, start=1):
            Center.objects.update_or_create(
                governorate=governorate,
                slug=f'{slug}-{position}',
                defaults={
                    'name_ar': center_name,
                    'name_en': center_name,
                    'is_active': True,
                },
            )


def unseed_locations(apps, schema_editor):
    Governorate = apps.get_model('sellers', 'Governorate')
    Governorate.objects.filter(slug__in=[item[3] for item in LOCATIONS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('sellers', '0004_governorate_icon_sellerprofile_experience_years_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_locations, unseed_locations),
    ]
