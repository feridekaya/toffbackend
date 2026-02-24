# TOFF — Modern Furniture eCommerce Platform

> Lüks ve modern mobilya deneyimini dijital dünyaya taşıyan full-stack e-ticaret platformu.  
> Backend: Django REST API · Frontend: React · Deploy: Railway

---

## 🗂 Proje Genel Bakış

TOFF, yüksek kaliteli mobilya ve ev dekorasyonu ürünlerini hedef alan, "Dark Luxury" estetik kimliğiyle tasarlanmış bir e-ticaret platformudur. Kullanıcılar ürünleri keşfedebilir, sepete ekleyebilir, kupon kullanarak sipariş verebilir ve sipariş durumlarını takip edebilir.

| Katman | Teknoloji | URL |
|---|---|---|
| Backend API | Django 5.2 + DRF | `web-production-4a117.up.railway.app` |
| Frontend | React | `tofffrontend-production.up.railway.app` |
| Veritabanı (prod) | PostgreSQL (Railway) | — |
| Veritabanı (dev) | SQLite | `db.sqlite3` |

---

## ✅ Tamamlanan Özellikler

### Auth & Kullanıcı
- [x] E-posta ile giriş (custom `EmailBackend`)
- [x] JWT kimlik doğrulama (`simplejwt` — access 60dk, refresh 7gün)
- [x] Custom JWT payload → `email`, `first_name`, `is_staff`
- [x] Token blacklist → güvenli logout (`POST /api/auth/logout/`)
- [x] Bcrypt şifre hashleme (birincil hasher)
- [x] Şifre sıfırlama e-posta akışı
- [x] Kullanıcı kaydı, profil görüntüleme/güncelleme/silme
- [x] Şifre değiştirme endpoint'i

### Ürün & Katalog
- [x] Ürün listeleme (sadece aktif), detay, CRUD (admin)
- [x] `is_active`, `discount_price`, `material`, `dimensions`, `weight` alanları
- [x] Kategori ve Koleksiyon CRUD (admin write, herkese read)

### Sipariş & Ödeme
- [x] Sipariş oluşturma (`POST /api/orders/create/`)
- [x] Kupon kodu doğrulama ve indirim hesaplama
- [x] `zip_code` ve `discount_amount` alanları
- [x] Sipariş durumu güncelleme (admin)
- [x] Iyzico ödeme entegrasyonu (test modu)

### Altyapı
- [x] Global error handler middleware (tutarlı JSON hata formatı)
- [x] Request loglama middleware
- [x] JWT auth check middleware
- [x] Custom DRF permission sınıfları (`IsOwnerOrAdmin`, `IsAdminOrReadOnly`, `IsActiveUser`)
- [x] E-posta altyapısı (Gmail SMTP, HTML şablonlar)
- [x] Railway deploy (Gunicorn + WhiteNoise)
- [x] README.md ve `.env.example` dokümantasyonu

---

## 🚀 Gelecek Planları

### 🔴 Yüksek Öncelik

#### 1. Iyzico Production Entegrasyonu
- `create_order` view'daki test ödeme fonksiyonu gerçek Iyzico API'siyle değiştirilecek
- Ödeme başarısız senaryoları için hata yönetimi eklenecek
- Webhook endpoint'i oluşturulacak (ödeme onayı / iade bildirimi)
- `Order` modeline `payment_status` ve `iyzico_payment_id` alanları eklenecek

#### 2. Rate Limiting & Throttling
- DRF `DEFAULT_THROTTLE_CLASSES` ayarlanacak
- Login endpoint'ine brute-force koruması (örn. dakikada 5 deneme)
- Public endpoint'lere anonim throttle, JWT'li kullanıcılara daha yüksek limit

#### 3. Sipariş E-posta Bildirimleri
- Sipariş oluşturulduğunda müşteriye otomatik onay e-postası
- Sipariş durumu "shipped" olduğunda kargo takip numarasıyla bildirim
- Admin'e yeni sipariş geldiğinde bildirim

---

### 🟡 Orta Öncelik

#### 4. Ürün Görselleri & Medya Yönetimi
- Çoklu ürün görseli desteği (`ProductImage` modeli)
- Cloudinary veya AWS S3 entegrasyonu (production'da Railway disk kalıcı değil)
- Görsel sıralama ve birincil görsel seçimi

#### 5. Gelişmiş Arama & Filtreleme
- Ürün arama (isim, açıklama, kategori)
- Fiyat aralığı, koleksiyon, malzeme filtresi
- Sıralama: fiyat, yenilik, popülerlik

#### 6. Stok Yönetimi
- `Product` modeline `stock_quantity` alanı
- Sipariş oluşturulduğunda stok güncellemesi
- Stok tükendiğinde ürün otomatik `is_active=False`
- Admin stok uyarı bildirimi

#### 7. Kullanıcı Yorumları & Puanlama
- `Review` modeli (ürün + kullanıcı + puan + yorum)
- Sadece ürünü satın almış kullanıcılar yorum yapabilir
- Ortalama puan hesaplama

---

### 🟢 Düşük Öncelik / Uzun Vade

#### 8. Admin Dashboard API
- Özet istatistikler: toplam gelir, sipariş sayısı, en çok satan ürünler
- Grafik verisi için zaman serisi endpoint'leri (günlük/haftalık/aylık)

#### 9. Favori Listesi Geliştirmeleri
- Birden fazla favori listesi (koleksiyon/liste adı)
- Favori listesini paylaşma linki

#### 10. Frontend Geliştirmeleri
- React Query ile server-state yönetimi
- Lazy loading & ürün listesi infinite scroll
- Ödeme akışı UI (Iyzico form entegrasyonu)
- Profil sayfası (sipariş geçmişi, adres yönetimi)
- PWA desteği (offline mod, bildirimler)

#### 11. Test Coverage
- Django `TestCase` ile unit testler (model, serializer, view)
- Pytest-django ile API entegrasyon testleri
- CI/CD pipeline (GitHub Actions → Railway otomatik deploy)

#### 12. Güvenlik Sertleştirme
- `CORS_ALLOW_ALL_ORIGINS = False` → sadece izin verilen originler
- HTTP güvenlik başlıkları (`SECURE_HSTS_SECONDS`, `X-Content-Type-Options`)
- API versiyonlama (`/api/v1/`)
- 2FA (İki Faktörlü Doğrulama) seçeneği

---

## 🗃 Veritabanı Şeması (Özet)

```
User (auth.User)
 ├── Profile          → avatar, updated_at
 └── Address[]        → birden fazla adres

Product
 ├── Category
 ├── Collection
 └── ProductImage[]   (planlanan)

Order
 ├── OrderItem[]      → product + quantity + price
 └── Coupon           → code, discount_type, amount

Cart
 └── CartItem[]       → product + quantity

Review (planlanan)
 └── User + Product + rating + comment
```

---

## 🔧 Geliştirici Notları

### Ortam Kurulumu
```bash
git clone https://github.com/feridekaya/toffbackend.git
cd toffbackend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env       # .env dosyasını düzenle
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Yeni Endpoint Eklerken
1. `models.py` → model değişikliği varsa `makemigrations` + `migrate`
2. `serializers.py` → serializer ekle/güncelle
3. `views.py` → view veya ViewSet yaz
4. `urls.py` → route ekle
5. Hata yönetimi DRF üzerinden otomatik (`custom_exception_handler`)
6. Permission için `api/permissions.py`'deki hazır sınıfları kullan

### Kod Standartları
- View'larda `try/except` yerine DRF exception'larını fırlat (`raise ValidationError(...)`)
- Business logic'i view yerine `serializer.validate_*` metodlarına koy
- Queryset'leri `get_queryset()` override ederek filtrele
- Admin işlemleri için `IsAdminUser` veya `IsAdminOrReadOnly` kullan
