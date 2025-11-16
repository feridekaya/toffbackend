from rest_framework import serializers
from .models import Product, Favorite  # models.py dosyamızdan Product modelini alıyoruz
from django.contrib.auth.models import User

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name','slug', 'description', 'price','image','category']
class UserSerializer(serializers.ModelSerializer):
    # 'write_only=True' şifrenin API'den geri okunmasını (GET) engeller
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        # Kayıt olurken hangi alanları isteyeceğimizi belirtir
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def create(self, validated_data):
        # 'create' metodunu eziyoruz ki şifreyi şifreleyerek (hash) kaydedebilelim
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class FavoriteReadSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    product = ProductSerializer(read_only=True) # <-- DEĞİŞİKLİK BURADA

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product', 'created_at']
class FavoriteWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['product']