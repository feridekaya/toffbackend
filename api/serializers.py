from rest_framework import serializers
# 'Favorite' modelini de import listesine ekle
from .models import Product, Category, Favorite 
from django.contrib.auth.models import User 

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        # 'slug' ve 'category' alanlarını React'e göndermek için ekliyoruz
        fields = ['id', 'name', 'slug', 'description', 'price', 'image', 'category']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

# === GÜNCELLENMİŞ FAVORİ SERIALIZER BÖLÜMÜ ===

# YENİ: Bu, favorileri OKURKEN kullanılacak (GET)
# (İç içe ProductSerializer kullanarak tam ürün bilgisini verir)
class FavoriteReadSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    # ProductSerializer'ı burada iç içe kullanarak
    # sadece ID'yi değil, tüm ürün objesini gönderiyoruz.
    product = ProductSerializer(read_only=True) 

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product', 'created_at']

# YENİ: Bu, favori OLUŞTURURKEN kullanılacak (POST)
# (Sadece ürünün ID'sini alır)
class FavoriteWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['product'] # Sadece 'product' ID'sini alır (user otomatiktir)