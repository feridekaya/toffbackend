<div align="center">

# 🖤 TOFF Backend API

**Django REST Framework · JWT Auth · PostgreSQL · Railway**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2-green?logo=django)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.16-red)](https://www.django-rest-framework.org)
[![JWT](https://img.shields.io/badge/Auth-JWT-orange)](https://django-rest-framework-simplejwt.readthedocs.io)
[![Railway](https://img.shields.io/badge/Deploy-Railway-purple?logo=railway)](https://railway.app)

</div>

---

## 📋 İçindekiler

- [Genel Bakış](#genel-bakış)
- [Teknoloji Stack](#teknoloji-stack)
- [Kurulum](#kurulum)
- [Ortam Değişkenleri](#ortam-değişkenleri)
- [API Referansı](#api-referansı)
- [Proje Yapısı](#proje-yapısı)
- [Deploy](#deploy)

---

## Genel Bakış

TOFF Design e-ticaret platformunun Django REST API backend'i.  
Ürün kataloğu, sipariş yönetimi, kullanıcı işlemleri ve kupon sistemi sunar.

---

## Teknoloji Stack

| Teknoloji | Versiyon | Kullanım |
|---|---|---|
| Python | 3.11 | Runtime |
| Django | 5.2 | Web framework |
| Django REST Framework | 3.16 | API katmanı |
| simplejwt | 5.5 | JWT kimlik doğrulama |
| bcrypt | 5.0 | Şifre hashleme |
| PostgreSQL | — | Production DB (Railway) |
| SQLite | — | Geliştirme DB |
| Gunicorn | 23.0 | WSGI sunucusu |
| WhiteNoise | 6.11 | Statik dosya servisi |
| Pillow | 12.0 | Görsel işleme |

---

## Kurulum

### Gereksinimler

- Python 3.11+
- pip
- Git

### 1. Repoyu Klonla

```bash
git clone https://github.com/your-username/toff-backend.git
cd toff-backend
```

### 2. Sanal Ortam Oluştur

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### 4. Ortam Değişkenlerini Ayarla

```bash
cp .env.example .env
# .env dosyasını kendi değerlerinizle düzenleyin
```

### 5. Veritabanı Migration

```bash
python manage.py migrate
```

### 6. Süper Kullanıcı Oluştur

```bash
python manage.py createsuperuser
```

### 7. Sunucuyu Başlat

```bash
python manage.py runserver
```

API `http://127.0.0.1:8000/` adresinde çalışır.  
Admin paneli: `http://127.0.0.1:8000/admin/`

---

## Ortam Değişkenleri

`.env` dosyası proje kökünde bulunmalıdır. Şablon için `.env.example`'a bakın.

| Değişken | Zorunlu | Açıklama |
|---|---|---|
| `SECRET_KEY` | ✅ | Django gizli anahtarı |
| `DEBUG` | ✅ | `True` (dev) / `False` (prod) |
| `ALLOWED_HOSTS` | ✅ | Virgülle ayrılmış host listesi |
| `DATABASE_URL` | ⬜ | PostgreSQL URL'si (boşsa SQLite) |
| `EMAIL_USER` | ⬜ | Gmail SMTP kullanıcısı |
| `EMAIL_PASS` | ⬜ | Gmail Uygulama Şifresi |

---

## API Referansı

Base URL: `https://web-production-4a117.up.railway.app`  
Tüm korumalı endpoint'ler `Authorization: Bearer <access_token>` başlığı gerektirir.

---

### Auth

| Method | Endpoint | Auth | Açıklama |
|---|---|---|---|
| `POST` | `/api/token/` | — | Giriş → access + refresh token |
| `POST` | `/api/token/refresh/` | — | Yeni access token al |
| `POST` | `/api/token/verify/` | — | Token geçerliliğini kontrol et |
| `POST` | `/api/auth/logout/` | JWT | Refresh token'ı geçersiz kıl |
| `POST` | `/api/register/` | — | Yeni kullanıcı kaydı |
| `POST` | `/api/auth/forgot-password/` | — | Şifre sıfırlama e-postası gönder |
| `POST` | `/api/auth/reset-password-confirm/<uid>/<token>/` | — | Şifreyi sıfırla |

**Login Request:**
```json
POST /api/token/
{
  "email": "user@example.com",
  "password": "secret"
}
```

**Login Response:**
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "Ali",
    "last_name": "Veli",
    "is_staff": false
  }
}
```

---

### Kullanıcı

| Method | Endpoint | Auth | Açıklama |
|---|---|---|---|
| `GET` | `/api/user/` | JWT | Profil bilgisi |
| `PUT / PATCH` | `/api/user/` | JWT | Profil güncelle |
| `DELETE` | `/api/user/` | JWT | Hesabı sil |
| `PUT` | `/api/change-password/` | JWT | Şifre değiştir |
| `GET` | `/api/users/` | Admin | Tüm kullanıcılar |

---

### Ürünler

| Method | Endpoint | Auth | Açıklama |
|---|---|---|---|
| `GET` | `/api/products/` | — | Ürün listesi (aktif) |
| `GET` | `/api/products/?is_active=all` | Admin | Tüm ürünler |
| `GET` | `/api/products/{id}/` | — | Ürün detayı |
| `POST` | `/api/products/` | Admin | Ürün oluştur |
| `PUT / PATCH` | `/api/products/{id}/` | Admin | Ürün güncelle |
| `DELETE` | `/api/products/{id}/` | Admin | Ürün sil |

---

### Kategoriler & Koleksiyonlar

| Method | Endpoint | Auth | Açıklama |
|---|---|---|---|
| `GET` | `/api/categories/` | — | Kategori listesi |
| `POST` | `/api/categories/` | Admin | Kategori oluştur |
| `PUT / DELETE` | `/api/categories/{slug}/` | Admin | Güncelle / Sil |
| `GET` | `/api/collections/` | — | Koleksiyon listesi |
| `POST` | `/api/collections/` | Admin | Koleksiyon oluştur |
| `PUT / DELETE` | `/api/collections/{slug}/` | Admin | Güncelle / Sil |

---

### Siparişler

| Method | Endpoint | Auth | Açıklama |
|---|---|---|---|
| `POST` | `/api/orders/create/` | — | Sipariş oluştur (kupon destekli) |
| `GET` | `/api/orders/` | JWT | Siparişlerim |
| `GET` | `/api/orders/{id}/` | JWT | Sipariş detayı |
| `PATCH` | `/api/orders/{id}/update_status/` | Admin | Durum güncelle |
| `DELETE` | `/api/orders/{id}/` | Admin | Sipariş sil |

**Sipariş Oluşturma:**
```json
POST /api/orders/create/
{
  "first_name": "Ali",
  "last_name": "Veli",
  "email": "ali@example.com",
  "phone": "5551234567",
  "address": "İstanbul",
  "city": "İstanbul",
  "zip_code": "34000",
  "country": "Turkey",
  "cart": [
    { "product_id": 1, "quantity": 2 }
  ],
  "coupon_code": "TOFF10"
}
```

---

### Kuponlar

| Method | Endpoint | Auth | Açıklama |
|---|---|---|---|
| `POST` | `/api/coupons/validate/` | — | Kupon doğrula |
| `GET` | `/api/coupons/` | Admin | Tüm kuponlar |
| `POST` | `/api/coupons/` | Admin | Kupon oluştur |
| `PUT / DELETE` | `/api/coupons/{id}/` | Admin | Güncelle / Sil |

---

### Sepet, Favoriler, Adresler

| Method | Endpoint | Auth | Açıklama |
|---|---|---|---|
| `GET` | `/api/cart/` | JWT | Sepet içeriği |
| `POST` | `/api/cart/add_item/` | JWT | Ürün ekle |
| `POST` | `/api/cart/remove_item/` | JWT | Ürün çıkar |
| `POST` | `/api/cart/update_quantity/` | JWT | Miktar güncelle |
| `GET / POST` | `/api/favorites/` | JWT | Favoriler |
| `DELETE` | `/api/favorites/{id}/` | JWT | Favoriden çıkar |
| `GET / POST` | `/api/addresses/` | JWT | Adresler |
| `PUT / DELETE` | `/api/addresses/{id}/` | JWT | Güncelle / Sil |

---

### İletişim

| Method | Endpoint | Auth | Açıklama |
|---|---|---|---|
| `POST` | `/api/contact/` | — | İletişim formu gönder |

---

### Hata Formatı

Tüm hata yanıtları aynı formattadır:

```json
{
  "success": false,
  "error": "Doğrulama Hatası",
  "detail": "Bu alan zorunludur.",
  "status_code": 400
}
```

| `status_code` | `error` |
|---|---|
| 400 | Doğrulama Hatası |
| 401 | Kimlik Doğrulama Gerekli |
| 403 | Bu İşlem İçin Yetkiniz Yok |
| 404 | Kaynak Bulunamadı |
| 429 | Çok Fazla İstek Gönderildi |
| 500 | Sunucu Hatası |

---

## Proje Yapısı

```
backend/
├── api/                        # Ana uygulama
│   ├── migrations/             # Veritabanı migration'ları
│   ├── admin.py                # Django admin
│   ├── backends.py             # Email ile giriş backend'i
│   ├── middleware.py           # Global error handler, request logging, JWT check
│   ├── models.py               # Veritabanı modelleri
│   ├── permissions.py          # Custom DRF permission sınıfları
│   ├── serializers.py          # DRF serializer'ları
│   ├── token_serializers.py    # Custom JWT claims
│   ├── urls.py                 # API URL'leri
│   └── views.py                # API view'ları
├── backend/                    # Django proje ayarları
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── utils/
│   └── email_helper.py         # E-posta gönderme yardımcısı
├── .env                        # Ortam değişkenleri (git'e eklenmez)
├── .env.example                # Ortam değişkeni şablonu
├── manage.py
├── Procfile                    # Railway / Heroku için
├── requirements.txt
└── runtime.txt                 # Python versiyonu
```

---

## Deploy

### Railway

1. [Railway](https://railway.app)'e yeni proje oluşturun
2. GitHub reponuzu bağlayın
3. **Environment Variables** ekleyin:
   - `SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-domain.up.railway.app`
   - `EMAIL_USER`, `EMAIL_PASS`
   - `DATABASE_URL` (Railway PostgreSQL servisi eklenirse otomatik gelir)
4. Deploy otomatik başlar

### Procfile

```
web: gunicorn backend.wsgi --log-file -
release: python manage.py migrate
```

---

## Frontend

TOFF Frontend (React): [tofffrontend-production.up.railway.app](https://tofffrontend-production.up.railway.app)

API Base URL (production): `https://web-production-4a117.up.railway.app`

---

<div align="center">
  <sub>Built with ❤️ by TOFF Design</sub>
</div>
