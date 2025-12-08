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
from .views import root_view

urlpatterns = [
    # 0. Root Path
    path('', root_view, name='root'),

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
from django.views.static import serve
from django.urls import re_path

# ...

# Her ortamda (Production dahil) medya dosyalarını sun
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]