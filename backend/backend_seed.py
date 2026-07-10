import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodmarket.settings')
django.setup()


def run():
    call_command('seed_marketplace')


if __name__ == '__main__':
    run()
