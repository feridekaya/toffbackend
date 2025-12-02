import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Category

# Eğer veritabanı boşsa veriyi yükle
if Category.objects.count() == 0:
    print("Loading initial data...")
    call_command('loaddata', 'railway_data.json')
    print("Initial data loaded successfully!")
else:
    print("Data already exists, skipping.")
