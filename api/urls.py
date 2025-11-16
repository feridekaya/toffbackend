# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views # views.py'den ProductViewSet'i alacak
from .views import UserCreateView # views.py'den UserCreateView'i alacak

# Ürünler için bir router oluştur (GET, POST, PUT, DELETE)
router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'favorites', views.FavoriteViewSet, basename='favorite')
# Ana adres listemiz
urlpatterns = [
    # 1. /api/register/ adresini Kayıt Olma kapısına bağla
    path('register/', UserCreateView.as_view(), name='user-register'),
    
    # 2. /api/products/ gibi adresleri router'a bağla
    path('', include(router.urls)),
]