from rest_framework import viewsets
from .models import Product, Category, Favorite # <-- 'Favorite' import edildi
# Serializer importlarını güncelle:
from .serializers import (
    ProductSerializer, UserSerializer, 
    FavoriteReadSerializer, FavoriteWriteSerializer # <-- Güncellendi
) 

from django.contrib.auth.models import User
from rest_framework import generics
# 'IsAuthenticated' (Kimliği Doğrulanmış) iznini import et
from rest_framework.permissions import AllowAny, IsAuthenticated 


# --- Ürünler için olan ViewSet (Değişiklik yok) ---
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all().order_by('-id')
        
        category_slug = self.request.query_params.get('category_slug')
        if category_slug is not None:
            queryset = queryset.filter(category__slug=category_slug)
            
        product_slug = self.request.query_params.get('slug')
        if product_slug is not None:
            queryset = queryset.filter(slug=product_slug)
            
        return queryset

# --- Kayıt Olma View'ı (Değişiklik yok) ---
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


# === GÜNCELLENMİŞ FAVORİ VİEWSET'İ (KAPI) ===
class FavoriteViewSet(viewsets.ModelViewSet):
    """
    Giriş yapmış kullanıcının kendi favorilerini 
    görmesi, eklemesi veya silmesi için API endpoint'i.
    """
    permission_classes = [IsAuthenticated] # Sadece giriş yapanlar erişebilir
    
    # YENİ FONKSİYON: Hangi serializer'ı kullanacağına karar ver
    def get_serializer_class(self):
        # Eğer istek 'list' (tüm favoriler) veya 'retrieve' (tek favori) ise:
        if self.action == 'list' or self.action == 'retrieve':
            return FavoriteReadSerializer # Tam ürün objesini gösteren OKUMA tercümanı
        # Eğer istek 'create' (yeni favori) veya 'update' ise:
        return FavoriteWriteSerializer # Sadece ID alan YAZMA tercümanı

    def get_queryset(self):
        # Kullanıcıları SADECE KENDİ favorilerini görecek şekilde filtrele
        return Favorite.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        # Yeni favori oluşturulurken 'user' alanını otomatik olarak ata
        serializer.save(user=self.request.user)