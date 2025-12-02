import os
import django

# Django ortamını ayarla
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Order, OrderItem, Address, Favorite, Coupon, Profile
from django.contrib.auth.models import User

def clean_database():
    print("Veritabanı temizliği başlıyor...")

    # 1. Siparişleri Sil
    print(f"Siliniyor: {Order.objects.count()} Sipariş...")
    Order.objects.all().delete()
    
    # 2. Adresleri Sil
    print(f"Siliniyor: {Address.objects.count()} Adres...")
    Address.objects.all().delete()

    # 3. Favorileri Sil
    print(f"Siliniyor: {Favorite.objects.count()} Favori...")
    Favorite.objects.all().delete()

    # 4. Kuponları Sil
    print(f"Siliniyor: {Coupon.objects.count()} Kupon...")
    Coupon.objects.all().delete()

    # 5. Profilleri Sil
    print(f"Siliniyor: {Profile.objects.count()} Profil...")
    Profile.objects.all().delete()

    # 6. Normal Kullanıcıları Sil (Süper kullanıcılar hariç)
    users_to_delete = User.objects.filter(is_superuser=False, is_staff=False)
    print(f"Siliniyor: {users_to_delete.count()} Normal Kullanıcı...")
    users_to_delete.delete()

    print("\nTEMİZLİK TAMAMLANDI!")
    print("Kalan Veriler:")
    print(f"- Kategoriler")
    print(f"- Koleksiyonlar")
    print(f"- Ürünler")
    print(f"- Süper Kullanıcılar: {User.objects.filter(is_superuser=True).count()}")

if __name__ == '__main__':
    clean_database()
