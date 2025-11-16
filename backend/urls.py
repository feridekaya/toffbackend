# backend/backend/urls.py
from django.contrib import admin
from django.urls import path, include

# Medya dosyalarını (resimler) sunmak için importlar
from django.conf import settings
from django.conf.urls.static import static

# Jeton (Token) sisteminin 'Giriş Yap' ve 'Yenile' görünümleri
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # 1. Admin Paneli
    path('admin/', admin.site.urls),
    
    # 2. /api/token/ (Giriş Yapma)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # 3. /api/token/refresh/ (Jeton Yenileme)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 4. /api/ ile başlayan diğer tüm istekleri api.urls'e yönlendir
    # (Bu, 'register' ve 'products' adreslerini kapsar)
    path('api/', include('api.urls')), 
]

# Sadece DEBUG modundayken medya dosyalarını (resimleri) sun
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)