import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Category
from django.utils.text import slugify

menu_data = [
  {
    'title': 'MASALAR',
    'slug': 'masalar',
    'subCategories': [
      { 'title': 'Yemek Masaları', 'slug': 'yemek-masalari' },
      { 'title': 'Çalışma & Ofis Masaları', 'slug': 'calisma-ofis' },
      { 'title': 'Mutfak Masaları', 'slug': 'mutfak-masalari' },
      { 'title': 'Toplantı Masaları', 'slug': 'toplanti-masalari' },
      { 'title': 'Bar Masaları', 'slug': 'bar-masalari' },
    ],
  },
  {
    'title': 'SEHPALAR',
    'slug': 'sehpalar',
    'subCategories': [
      { 'title': 'Orta Sehpalar', 'slug': 'orta-sehpalar' },
      { 'title': 'Yan Sehpalar', 'slug': 'yan-sehpalar' },
      { 'title': 'Dresuarlar', 'slug': 'dresuarlar' },
    ],
  },
  {
    'title': 'OTURMA ELEMANLARI',
    'slug': 'oturma-elemanlari',
    'subCategories': [
      { 'title': 'Sandalyeler', 'slug': 'sandalyeler' },
      { 'title': 'Banklar (Benchler)', 'slug': 'banklar' },
      { 'title': 'Bar Tabureleri', 'slug': 'bar-tabureleri' },
      { 'title': 'Tabureler', 'slug': 'tabureler' },
    ],
  },
  {
    'title': 'DEPOLAMA & DÜZENLEME',
    'slug': 'depolama',
    'subCategories': [
      { 'title': 'Kitaplıklar', 'slug': 'kitapliklar' },
      { 'title': 'TV Üniteleri', 'slug': 'tv-uniteleri' },
      { 'title': 'Duvar Rafları', 'slug': 'duvar-raflari' },
      { 'title': 'Askılıklar', 'slug': 'askiliklar' },
      { 'title': 'Antre Çözümleri / Ayakkabılık', 'slug': 'antre' },
      { 'title': 'Havluluklar', 'slug': 'havluluklar' },
    ],
  },
  {
    'title': 'DIŞ MEKAN (OUTDOOR)',
    'slug': 'dis-mekan',
    'subCategories': [
      { 'title': 'Dış Mekan Masaları', 'slug': 'masalar' },
      { 'title': 'Dış Mekan Sandalyeleri', 'slug': 'sandalyeler' },
      { 'title': 'Dış Mekan Oturma Grubu', 'slug': 'oturma-grubu' },
      { 'title': 'Şezlonglar', 'slug': 'sezlonglar' },
      { 'title': 'Salıncaklar', 'slug': 'salincaklar' },
    ],
  },
  {
    'title': 'AKSESUAR & TAMAMLAYICI',
    'slug': 'aksesuar',
    'subCategories': [
      { 'title': 'Saksılıklar', 'slug': 'saksiliklar' },
      { 'title': 'Aydınlatma (Lambaderler)', 'slug': 'aydinlatma' },
      { 'title': 'Şamdanlar', 'slug': 'samdanlar' },
    ],
  },
]

for item in menu_data:
    # Ana kategori oluştur (Parent yok)
    parent_cat, created = Category.objects.get_or_create(
        slug=item['slug'],
        defaults={'name': item['title']}
    )
    if created:
        print(f"Created parent category: {item['title']}")
    else:
        print(f"Parent category exists: {item['title']}")

    # Alt kategorileri oluştur
    for sub in item['subCategories']:
         sub_cat, created = Category.objects.get_or_create(
            slug=sub['slug'],
            defaults={'name': sub['title'], 'parent': parent_cat}
        )
            
         if created:
            print(f"  Created sub category: {sub['title']}")
         else:
            print(f"  Sub category exists: {sub['title']}")
