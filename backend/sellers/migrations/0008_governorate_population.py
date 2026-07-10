from datetime import date

from django.db import migrations


# CAPMAS official estimates as of 2023-07-01. A single reference date is used
# across all governorates so population ordering remains internally comparable.
POPULATIONS = {
    'القاهرة': 10_248_385,
    'الجيزة': 9_514_540,
    'الشرقية': 7_909_342,
    'الدقهلية': 7_050_004,
    'البحيرة': 6_878_289,
    'المنيا': 6_337_595,
    'القليوبية': 6_137_688,
    'سوهاج': 5_727_271,
    'الإسكندرية': 5_546_663,
    'الغربية': 5_439_085,
    'أسيوط': 5_061_934,
    'المنوفية': 4_736_945,
    'الفيوم': 4_080_645,
    'كفر الشيخ': 3_718_316,
    'قنا': 3_640_916,
    'بني سويف': 3_592_039,
    'أسوان': 1_656_218,
    'دمياط': 1_618_239,
    'الإسماعيلية': 1_452_743,
    'الأقصر': 1_400_640,
    'السويس': 792_551,
    'بورسعيد': 791_749,
    'مطروح': 547_702,
    'شمال سيناء': 508_109,
    'البحر الأحمر': 403_077,
    'الوادي الجديد': 266_926,
    'جنوب سيناء': 116_479,
}


def populate_governorate_population(apps, schema_editor):
    Governorate = apps.get_model('sellers', 'Governorate')
    reference_date = date(2023, 7, 1)
    for name, population in POPULATIONS.items():
        Governorate.objects.filter(name_ar=name).update(
            estimated_population=population,
            population_as_of=reference_date,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('sellers', '0007_alter_governorate_options_and_more'),
    ]

    operations = [
        migrations.RunPython(
            populate_governorate_population,
            migrations.RunPython.noop,
        ),
    ]
