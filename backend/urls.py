# backend/backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

# Özel JWT view (custom claims: email, is_staff vs.)
from api.token_serializers import CustomTokenObtainPairView

# Standart simplejwt view'ları
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

# Logout (blacklist) view
from rest_framework_simplejwt.views import TokenBlacklistView

from .views import root_view

urlpatterns = [
    # 0. Root
    path('', root_view, name='root'),

    # 1. Admin
    path('admin/', admin.site.urls),

    # 2. JWT Auth Endpoint'leri
    path('api/token/',         CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # POST: login
    path('api/token/refresh/', TokenRefreshView.as_view(),          name='token_refresh'),       # POST: refresh
    path('api/token/verify/',  TokenVerifyView.as_view(),           name='token_verify'),        # POST: doğrula
    path('api/auth/logout/',   TokenBlacklistView.as_view(),        name='token_blacklist'),     # POST: logout

    # 3. API
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