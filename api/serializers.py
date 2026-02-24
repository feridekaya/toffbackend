# C:\Users\kayaf\backend\api\serializers.py
from rest_framework import serializers
from .models import Product, Category, Collection, Favorite, Profile, Address, ProductImage, ProductSize, ProductColor, Coupon, Cart, CartItem, Order, OrderItem
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
        fields = ['phone_number', 'birth_date', 'gender', 'avatar', 'updated_at']
        read_only_fields = ['updated_at']


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

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email']

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    uidb64 = serializers.CharField(read_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Şifreler eşleşmiyor.")
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
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'discount_price',
            'image', 'category', 'collection', 'stock', 'is_active',
            'material', 'dimensions', 'weight',
            'created_at', 'images', 'sizes', 'colors'
        ]

class CategorySerializer(serializers.ModelSerializer):
    header_slug = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'header_slug']

    def get_header_slug(self, obj):
        # Eğer bir üst kategori varsa onun slug'ını, yoksa kendininkini döndür
        if obj.parent:
            return obj.parent.slug
        return obj.slug


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

# --- SEPET İÇİN ---

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    selected_size = ProductSizeSerializer(read_only=True)
    selected_size_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductSize.objects.all(), source='selected_size', write_only=True, allow_null=True, required=False
    )
    selected_color = ProductColorSerializer(read_only=True)
    selected_color_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductColor.objects.all(), source='selected_color', write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'selected_size', 'selected_size_id', 'selected_color', 'selected_color_id']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'updated_at']

# --- SİPARİŞLER İÇİN ---

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 'quantity', 'price', 'selected_size', 'selected_color']

    def get_product_image(self, obj):
        if obj.product and obj.product.image:
            return obj.product.image.url
        return None

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.ReadOnlyField(source='user.email')
    coupon_code = serializers.ReadOnlyField(source='coupon.code')

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_email', 'full_name', 'address', 'city', 'zip_code', 'phone',
            'total_amount', 'coupon', 'coupon_code', 'discount_amount',
            'status', 'created_at', 'items',
            'customer_note', 'tracking_number'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'total_amount', 'items', 'coupon_code']
