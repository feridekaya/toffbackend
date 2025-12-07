# C:\Users\kayaf\backend\api\serializers.py
from rest_framework import serializers
from .models import Product, Category, Collection, Favorite, Profile, Address, ProductImage, ProductSize, ProductColor, Coupon
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password 


# --- KAYIT İÇİN ---
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'phone_number')

    def create(self, validated_data):
        email = validated_data['email']
        phone_number = validated_data.pop('phone_number')
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        if hasattr(user, 'profile'):
            user.profile.phone_number = phone_number
            user.profile.save()
            
        return user


# --- KULLANICI BİLGİLERİM SAYFASI İÇİN ---

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone_number', 'birth_date', 'gender']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()

        profile = instance.profile
        profile.phone_number = profile_data.get('phone_number', profile.phone_number)
        
        birth_date_data = profile_data.get('birth_date', profile.birth_date)
        profile.birth_date = birth_date_data if birth_date_data else None
        
        profile.gender = profile_data.get('gender', profile.gender)
        profile.save()

        return instance 


# --- ŞİFRE DEĞİŞTİRME İÇİN ---

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Yeni şifreler eşleşmiyor."})
        
        validate_password(data['new_password'])
        
        return data


# --- ÜRÜN VE KATEGORİLER İÇİN ---

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ['id', 'name', 'price']

class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ['id', 'name', 'hex_code']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    sizes = ProductSizeSerializer(many=True, read_only=True)
    colors = ProductColorSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'image', 'category', 'collection', 'created_at', 'images', 'sizes', 'colors']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent']


# --- KOLEKSİYONLAR İÇİN ---

class CollectionSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Collection
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active', 'order', 'product_count', 'created_at']
    
    def get_product_count(self, obj):
        return obj.products.count()


# --- FAVORİLER İÇİN ---

class FavoriteReadSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    product = ProductSerializer(read_only=True) 

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product', 'created_at']

class FavoriteWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['product']

# --- ADRESLER İÇİN ---

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ('user', 'created_at')
        extra_kwargs = {
            'tc_id': {'required': False, 'allow_blank': True, 'allow_null': True},
            'corporate_name': {'required': False, 'allow_blank': True, 'allow_null': True},
            'tax_office': {'required': False, 'allow_blank': True, 'allow_null': True},
            'tax_number': {'required': False, 'allow_blank': True, 'allow_null': True},
        }

# --- KUPONLAR İÇİN ---

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'