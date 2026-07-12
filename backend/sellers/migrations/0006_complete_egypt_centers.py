from django.db import migrations


# Egypt's 185 markaz-level administrative units in the 22 governorates that
# use markaz divisions. Names omit the repeated "مركز" prefix for cleaner UI.
MARKAZES = {
    'الجيزة': ['البدرشين', 'الصف', 'أطفيح', 'العياط', 'الواحات البحرية', 'منشأة القناطر', 'أوسيم', 'كرداسة', 'أبو النمرس'],
    'القليوبية': ['بنها', 'قليوب', 'القناطر الخيرية', 'الخانكة', 'كفر شكر', 'طوخ', 'شبين القناطر'],
    'الإسكندرية': ['برج العرب'],
    'البحيرة': ['دمنهور', 'كفر الدوار', 'رشيد', 'إدكو', 'أبو المطامير', 'أبو حمص', 'الدلنجات', 'المحمودية', 'الرحمانية', 'إيتاي البارود', 'حوش عيسى', 'شبراخيت', 'كوم حمادة', 'بدر', 'وادي النطرون'],
    'مطروح': ['مرسى مطروح', 'الحمام', 'العلمين', 'الضبعة', 'النجيلة', 'سيدي براني', 'السلوم', 'سيوة'],
    'دمياط': ['دمياط', 'فارسكور', 'كفر سعد', 'الزرقا', 'كفر البطيخ'],
    'الدقهلية': ['المنصورة', 'طلخا', 'ميت غمر', 'دكرنس', 'أجا', 'منية النصر', 'السنبلاوين', 'بني عبيد', 'المنزلة', 'تمي الأمديد', 'الجمالية', 'شربين', 'المطرية', 'بلقاس', 'ميت سلسيل', 'محلة دمنة', 'نبروه'],
    'كفر الشيخ': ['كفر الشيخ', 'دسوق', 'فوه', 'مطوبس', 'البرلس', 'الحامول', 'بيلا', 'الرياض', 'سيدي سالم', 'قلين'],
    'الغربية': ['طنطا', 'المحلة الكبرى', 'كفر الزيات', 'زفتى', 'السنطة', 'قطور', 'بسيون', 'سمنود'],
    'المنوفية': ['شبين الكوم', 'السادات', 'منوف', 'أشمون', 'الباجور', 'قويسنا', 'بركة السبع', 'تلا', 'الشهداء'],
    'الشرقية': ['الزقازيق', 'منيا القمح', 'بلبيس', 'مشتول السوق', 'أبو حماد', 'ههيا', 'أبو كبير', 'فاقوس', 'الإبراهيمية', 'ديرب نجم', 'كفر صقر', 'أولاد صقر', 'الحسينية'],
    'الإسماعيلية': ['الإسماعيلية', 'فايد', 'القنطرة شرق', 'القنطرة غرب', 'التل الكبير', 'أبو صوير', 'القصاصين'],
    'شمال سيناء': ['العريش', 'الشيخ زويد', 'رفح', 'بئر العبد', 'الحسنة', 'نخل'],
    'بني سويف': ['بني سويف', 'الواسطى', 'ناصر', 'إهناسيا', 'ببا', 'سمسطا', 'الفشن'],
    'الفيوم': ['الفيوم', 'طامية', 'سنورس', 'إطسا', 'إبشواي', 'يوسف الصديق'],
    'المنيا': ['المنيا', 'العدوة', 'مغاغة', 'بني مزار', 'مطاي', 'سمالوط', 'أبو قرقاص', 'ملوي', 'دير مواس'],
    'أسيوط': ['أسيوط', 'ديروط', 'منفلوط', 'القوصية', 'أبنوب', 'أبو تيج', 'الغنايم', 'ساحل سليم', 'البداري', 'صدفا', 'الفتح'],
    'الوادي الجديد': ['الخارجة', 'باريس', 'الداخلة', 'الفرافرة', 'بلاط'],
    'سوهاج': ['سوهاج', 'أخميم', 'البلينا', 'المراغة', 'المنشأة', 'دار السلام', 'جرجا', 'جهينة', 'ساقلته', 'طما', 'طهطا', 'العسيرات'],
    'قنا': ['قنا', 'أبو تشت', 'نجع حمادي', 'دشنا', 'الوقف', 'قفط', 'نقادة', 'قوص', 'فرشوط'],
    'الأقصر': ['الزينية', 'البياضية', 'القرنة', 'أرمنت', 'الطود', 'إسنا'],
    'أسوان': ['أسوان', 'دراو', 'كوم أمبو', 'نصر النوبة', 'إدفو'],
}


# Urban governorates use districts/cities rather than markaz divisions. These
# additions keep the location picker useful and complete for marketplace users.
URBAN_ADDITIONS = {
    'القاهرة': [
        'شبرا', 'الزاوية الحمراء', 'حدائق القبة', 'روض الفرج', 'الشرابية',
        'الساحل', 'الزيتون', 'الأميرية', 'الوايلي', 'مصر الجديدة', 'النزهة',
        'شرق مدينة نصر', 'غرب مدينة نصر', 'السلام أول', 'السلام ثان',
        'المطرية', 'المرج', 'القاهرة الجديدة', 'منشأة ناصر', 'وسط القاهرة',
        'الدرب الأحمر', 'الجمالية', 'بولاق', 'غرب القاهرة', 'عابدين',
        'الأزبكية', 'الموسكي', 'باب الشعرية', 'السيدة زينب', 'مصر القديمة',
        'الخليفة', 'المقطم', 'البساتين', 'دار السلام', 'المعادي', 'طرة',
        'المعصرة', 'التبين', '15 مايو',
    ],
    'بورسعيد': ['غرب', 'جنوب'],
    'البحر الأحمر': ['حلايب'],
    'جنوب سيناء': ['طابا', 'أبو رديس', 'أبو زنيمة'],
}


def add_complete_centers(apps, schema_editor):
    Governorate = apps.get_model('sellers', 'Governorate')
    Center = apps.get_model('sellers', 'Center')
    all_locations = {
        name: centers + URBAN_ADDITIONS.get(name, [])
        for name, centers in MARKAZES.items()
    }
    for name, additions in URBAN_ADDITIONS.items():
        all_locations.setdefault(name, additions)

    for governorate_name, names in all_locations.items():
        governorate = Governorate.objects.filter(name_ar=governorate_name).first()
        if not governorate:
            continue
        existing = {
            center.name_ar.removeprefix('مركز ').strip()
            for center in Center.objects.filter(governorate=governorate)
        }
        next_position = Center.objects.filter(governorate=governorate).count() + 1
        for name in names:
            normalized = name.removeprefix('مركز ').strip()
            if normalized in existing:
                continue
            Center.objects.create(
                governorate=governorate,
                name_ar=normalized,
                name_en=normalized,
                slug=f'{governorate.slug}-complete-{next_position}',
                is_active=True,
            )
            existing.add(normalized)
            next_position += 1


class Migration(migrations.Migration):
    dependencies = [
        ('sellers', '0005_seed_egypt_locations'),
    ]

    operations = [
        migrations.RunPython(add_complete_centers, migrations.RunPython.noop),
    ]
