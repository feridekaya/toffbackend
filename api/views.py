from rest_framework import viewsets
from .models import Product, Category, Favorite # <-- Category'yi import et
from .serializers import (
    ProductSerializer, UserSerializer, 
    FavoriteReadSerializer, FavoriteWriteSerializer
)
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    """
    Tüm ürünleri almak ve oluşturmak için bir API endpoint'i.
    """
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer

    # YENİ: Bu fonksiyonu ekleyerek varsayılan 'queryset'i eziyoruz
    def get_queryset(self):
        """
        Bu görünümü, URL'deki 'category_slug' parametresine 
        göre filtreleyecek şekilde dinamik olarak ayarlar.
        """
        queryset = Product.objects.all().order_by('-id') # Varsayılan olarak tüm ürünler
        
        # URL'den 'category_slug' parametresini almaya çalış
        category_slug = self.request.query_params.get('category_slug')
        
        # Eğer 'category_slug' parametresi varsa...
        if category_slug is not None:
            # ...queryset'i, o slug'a ait kategorideki ürünlerle filtrele
            queryset = queryset.filter(category__slug=category_slug)
            
        product_slug = self.request.query_params.get('slug')
        if product_slug is not None:
            queryset = queryset.filter(slug=product_slug)
            
        return queryset
class UserCreateView(generics.CreateAPIView):
    """
    Yeni bir kullanıcı oluşturmak için bir API endpoint'i (Kayıt Ol).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny] # <-- Herkesin (giriş yapmayanların da) bu adrese erişmesine izin ver
class FavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated] 
    
    # serializer_class = FavoriteSerializer <-- BU ESKİ SATIRI SİL
    
    # YENİ FONKSİYON: Hangi serializer'ı kullanacağına karar ver
    def get_serializer_class(self):
        # Eğer istek 'list' (tüm favoriler) veya 'retrieve' (tek favori) ise:
        if self.action == 'list' or self.action == 'retrieve':
            return FavoriteReadSerializer # Tam ürün objesini gösteren OKUMA tercümanı
        # Eğer istek 'create' (yeni favori) ise:
        return FavoriteWriteSerializer # Sadece ID alan YAZMA tercümanı

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)