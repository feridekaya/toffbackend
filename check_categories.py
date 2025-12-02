import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Category

def list_categories():
    categories = Category.objects.all()
    print(f"Toplam Kategori: {categories.count()}")
    for cat in categories:
        parent_name = cat.parent.name if cat.parent else "Yok"
        print(f"- {cat.name} (Slug: {cat.slug}, Parent: {parent_name})")

if __name__ == '__main__':
    list_categories()
