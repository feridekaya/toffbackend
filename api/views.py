from rest_framework import viewsets, generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action, api_view, permission_classes
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction

from .models import Product, Category, Collection, Favorite, Address, Coupon, Order, OrderItem
from .serializers import (
    ProductSerializer, CollectionSerializer, UserSerializer, RegisterSerializer,
    FavoriteReadSerializer, FavoriteWriteSerializer, 
    ChangePasswordSerializer, AddressSerializer, CouponSerializer, CategorySerializer,
    OrderSerializer
)
from . import iyzico_service

# --- Pagination Class ---
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 24
    page_size_query_param = 'page_size'
    max_page_size = 100

# --- Ürünler için olan ViewSet ---
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-id']
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        # 1. Kategori Filtresi
        category_slug = self.request.query_params.get('category_slug')
        if category_slug:
            if category_slug == 'tum-urunler':
                pass # Filtreleme yapma, hepsini getir
            elif category_slug == 'yeni-gelenler':
                queryset = queryset.order_by('-created_at') # En yeniler en başta
            else:
                # Kategori ve alt kategorilerini kapsayacak şekilde filtrele
                try:
                    category = Category.objects.get(slug=category_slug)
                    
                    # Yardımcı fonksiyon: Alt kategorileri rekürsif olarak bul
                    def get_category_ids(cat):
                        ids = [cat.id]
                        for sub in cat.subcategories.all():
                            ids.extend(get_category_ids(sub))
                        return ids
                    
                    all_ids = get_category_ids(category)
                    queryset = queryset.filter(category__id__in=all_ids)
                    
                except Category.DoesNotExist:
                    queryset = queryset.none()
        
        # 2. Koleksiyon Filtresi
        collection_slug = self.request.query_params.get('collection_slug')
        if collection_slug:
            try:
                collection = Collection.objects.get(slug=collection_slug, is_active=True)
                queryset = queryset.filter(collection=collection)
            except Collection.DoesNotExist:
                queryset = queryset.none()
            
        # 3. Ürün Slug Filtresi (Detay sayfası için)
        product_slug = self.request.query_params.get('slug')
        if product_slug is not None:
            queryset = queryset.filter(slug=product_slug)

        # 4. Arama (Search) Filtresi
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
            
        return queryset


# --- Kategoriler ViewSet ---
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    pagination_class = None  # Kategoriler için sayfalama kapatılabilir veya büyük tutulabilir


# --- Koleksiyonlar ViewSet ---
class CollectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Koleksiyonları listeler ve detaylarını gösterir.
    Sadece aktif koleksiyonlar gösterilir.
    """
    queryset = Collection.objects.filter(is_active=True).order_by('order', 'name')
    serializer_class = CollectionSerializer
    lookup_field = 'slug'
    
    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """
        Belirli bir koleksiyonun ürünlerini döndürür
        URL: /api/collections/{slug}/products/
        """
        collection = self.get_object()
        products = collection.products.all()
        
        # Pagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(products, request)
        
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


# --- Kayıt Olma View'ı ---
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# --- Favoriler ViewSet ---
class FavoriteViewSet(viewsets.ModelViewSet):
    """
    Giriş yapmış kullanıcının kendi favorilerini 
    görmesi, eklemesi veya silmesi için API endpoint'i.
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return FavoriteReadSerializer
        return FavoriteWriteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# --- Şifre Değiştirme View ---
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        return self.request.user


# --- SİPARİŞ YÖNETİMİ (ADMIN) ---
class OrderViewSet(viewsets.ModelViewSet):
    """
    Admin sipariş yönetimi için ViewSet.
    Kullanıcılar sadece kendi siparişlerini görebilir (list/retrieve).
    Admin (staff) tüm siparişleri görebilir, durumunu değiştirebilir.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Eğer admin/staff ise tüm siparişler
        if user.is_staff:
            return Order.objects.all().order_by('-created_at')
        # Değilse sadece kendi siparişleri
        return Order.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        # API üzerinden sipariş oluşturulursa (genelde create_order view kullanılır ama burası yedek)
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Admin'in sipariş durumunu güncellemesi için endpoint.
        PATCH /api/orders/{id}/update_status/
        Body: { "status": "preparing", "tracking_number": "TRK123" }
        """
        if not request.user.is_staff:
            return Response({'error': 'Yetkiniz yok.'}, status=status.HTTP_403_FORBIDDEN)
        
        order = self.get_object()
        new_status = request.data.get('status')
        tracking_number = request.data.get('tracking_number')

        if new_status:
            order.status = new_status
            
            # DURUM DEĞİŞİKLİĞİ EMAİLİ (Sadece 'shipped' için)
            if new_status == 'shipped' and order.user and order.user.email:
                send_toff_email(
                    to_email=order.user.email,
                    subject="Siparişiniz Yola Çıktı! 🚚",
                    context={
                        'full_name': order.full_name,
                        'order_id': order.id,
                        'tracking_number': tracking_number or 'Belirtilmedi',
                    },
                    template_type='order_shipped'
                )
        
        if tracking_number is not None:
            order.tracking_number = tracking_number

        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Eski şifre yanlış."]}, status=status.HTTP_400_BAD_REQUEST)
            
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"detail": "Şifre başarıyla güncellendi."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- Adresler ViewSet ---
class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# --- Kupon Doğrulama ---
@api_view(['POST'])
@permission_classes([AllowAny])
def validate_coupon(request):
    code = request.data.get('code')
    if not code:
        return Response({'error': 'Kupon kodu gereklidir.'}, status=400)

    try:
        coupon = Coupon.objects.get(code=code.upper())
    except Coupon.DoesNotExist:
        return Response({'error': 'Geçersiz kupon kodu.'}, status=404)

    if not coupon.is_active:
        return Response({'error': 'Bu kupon artık aktif değil.'}, status=400)

    now = timezone.now()
    if now < coupon.valid_from or now > coupon.valid_to:
        return Response({'error': 'Bu kuponun süresi dolmuş veya henüz başlamamış.'}, status=400)

    if coupon.usage_limit is not None and coupon.used_count >= coupon.usage_limit:
        return Response({'error': 'Bu kuponun kullanım limiti dolmuş.'}, status=400)

    serializer = CouponSerializer(coupon)
    return Response(serializer.data)

# --- Sipariş Oluşturma ---
@api_view(['POST'])
@permission_classes([AllowAny])
def create_order(request):
    """
    Sipariş oluşturma view'i
    1. Stok kontrolü
    2. Ödeme işlemi (Iyzico)
    3. Sipariş kaydı ve stok düşme
    """
    
    # Gelen verileri al
    full_name = request.data.get('full_name')
    address = request.data.get('address')
    city = request.data.get('city')
    phone = request.data.get('phone')
    cart_items = request.data.get('cart_items', [])
    
    # Kart bilgileri (opsiyonel - test için)
    card_info = request.data.get('card_info', {})
    
    # Validasyon
    if not all([full_name, address, city, phone]):
        return Response({
            'error': 'Lütfen tüm teslimat bilgilerini doldurunuz.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not cart_items:
        return Response({
            'error': 'Sepetiniz boş.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 1. STOK KONTROLÜ
    out_of_stock_products = []
    total_amount = 0
    
    for item in cart_items:
        product_id = item.get('product', {}).get('id')
        quantity = item.get('quantity', 0)
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Stok kontrolü
            if product.stock < quantity:
                out_of_stock_products.append({
                    'product': product.name,
                    'requested': quantity,
                    'available': product.stock
                })
            
            # Toplam tutarı hesapla
            total_amount += float(product.price) * quantity
            
        except Product.DoesNotExist:
            return Response({
                'error': f'Ürün bulunamadı: ID {product_id}'
            }, status=status.HTTP_404_NOT_FOUND)
    
    # Stok yetersizse hata döndür
    if out_of_stock_products:
        return Response({
            'error': 'Bazı ürünlerin stoğu yetersiz.',
            'out_of_stock': out_of_stock_products
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 2. ÖDEME İŞLEMİ (Iyzico)
    # Test modunda çalışıyoruz - gerçek kart bilgileri gerekmez
    payment_result = iyzico_service.create_test_payment_success(total_amount)
    
    # Gerçek Iyzico entegrasyonu için:
    # payment_result = iyzico_service.create_payment(
    #     cart_items=cart_items,
    #     total_amount=total_amount,
    #     card_info=card_info,
    #     billing_info={
    #         'full_name': full_name,
    #         'address': address,
    #         'city': city,
    #         'phone': phone
    #     }
    # )
    
    # Ödeme başarısız olursa
    if not payment_result.get('success'):
        return Response({
            'error': 'Ödeme işlemi başarısız oldu.',
            'detail': payment_result.get('error_message')
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 3. SİPARİŞ KAYDI VE STOK DÜŞME
    try:
        with transaction.atomic():
            # Siparişi oluştur
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=full_name,
                address=address,
                city=city,
                phone=phone,
                total_amount=total_amount,
                status='paid',
                payment_id=payment_result.get('payment_id'),
                customer_note=request.data.get('customer_note', '') # Müşteri notunu kaydet
            )
            
            # Sipariş ürünlerini kaydet ve stokları düş
            for item in cart_items:
                product_id = item.get('product', {}).get('id')
                quantity = item.get('quantity', 0)
                
                # Varyasyon bilgilerini al (Snapshot için)
                selected_size_obj = item.get('selectedSize') or item.get('selected_size')
                selected_color_obj = item.get('selectedColor') or item.get('selected_color')

                size_name = selected_size_obj.get('name') if selected_size_obj else None
                color_name = selected_color_obj.get('name') if selected_color_obj else None
                
                product = Product.objects.select_for_update().get(id=product_id)
                
                # Sipariş ürünü oluştur
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    quantity=quantity,
                    price=product.price,
                    selected_size=size_name,   # Snapshot
                    selected_color=color_name  # Snapshot
                )
                
                # Stoktan düş
                product.stock -= quantity
                product.save()
            
            return Response({
                'success': True,
                'message': 'Siparişiniz başarıyla alındı!',
                'order_id': order.id,
                'payment_id': payment_result.get('payment_id')
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({
            'error': 'Sipariş oluşturulurken bir hata oluştu.',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- Sepet ViewSet ---
from .models import Cart, CartItem, ProductSize, ProductColor
from .serializers import CartSerializer, CartItemSerializer

class CartViewSet(viewsets.ModelViewSet):
    """
    Kullanıcının sepetini yönetir.
    GET /api/cart/ -> Sepeti getirir (yoksa oluşturur)
    POST /api/cart/add_item/ -> Ürün ekler
    POST /api/cart/remove_item/ -> Ürün siler
    POST /api/cart/update_quantity/ -> Miktar günceller
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        size_id = request.data.get('selected_size_id')
        color_id = request.data.get('selected_color_id')

        if not product_id:
            return Response({'error': 'Product ID required'}, status=400)

        product = Product.objects.get(id=product_id)
        
        # Varyasyonları bul
        size = None
        if size_id:
            size = ProductSize.objects.get(id=size_id)
            
        color = None
        if color_id:
            color = ProductColor.objects.get(id=color_id)

        # Aynı varyasyona sahip ürün var mı?
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            selected_size=size,
            selected_color=color,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        # Güncel sepeti döndür
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        item_id = request.data.get('item_id')

        if not item_id:
             return Response({'error': 'Item ID required'}, status=400)

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
            item.delete()
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=404)

        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))

        if not item_id:
             return Response({'error': 'Item ID required'}, status=400)
        
        if quantity < 1:
            return Response({'error': 'Quantity must be at least 1'}, status=400)

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
            item.quantity = quantity
            item.save()
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=404)

        serializer = self.get_serializer(cart)
        return Response(serializer.data)
# --- İLETİŞİM FORMU ---
from .utils.email_helper import send_toff_email

class ContactView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        subject = request.data.get('subject')
        message = request.data.get('message')
        
        if not all([name, email, subject, message]):
            return Response({'error': 'Lütfen tüm alanları doldurunuz.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Admin'e E-posta Gönder
        email_sent = send_toff_email(
            to_email='thetoffdesign@gmail.com', # Admin Email
            subject=f"TOFF İletişim: {subject} - {name}",
            context={
                'name': name,
                'email': email,
                'user_subject': subject,
                'message': message
            },
            template_type='contact_form'
        )
        
        if email_sent:
            return Response({'success': True, 'message': 'Mesajınız iletildi.'})
        else:
            return Response({'error': 'Mesaj gönderilemedi. Lütfen daha sonra tekrar deneyiniz.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- Şifre Sıfırlama (Forgot Password) Views ---
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .serializers import ForgotPasswordSerializer, ResetPasswordSerializer

# Frontend URL (Environment variable or hardcoded for now)
# FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://tofffrontend-production.up.railway.app')
FRONTEND_URL = 'https://tofffrontend-production.up.railway.app' 

class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                
                # Token ve UID oluştur
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                
                # Link oluştur
                reset_link = f"{FRONTEND_URL}/reset-password?uid={uid}&token={token}"
                
                # Email Gönder
                send_toff_email(
                    to_email=user.email,
                    subject="Şifrenizi mi unuttunuz?",
                    context={'reset_link': reset_link},
                    template_type='password_reset'
                )
                
            except User.DoesNotExist:
                # Güvenlik için kullanıcı bulunamasa bile başarılı gibi davran
                pass
            
            return Response({'success': 'Eğer kayıtlı bir hesabınız varsa, şifre sıfırlama bağlantısı e-posta adresinize gönderildi.'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordConfirmView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = str(urlsafe_base64_decode(uidb64), 'utf-8')
                user = User.objects.get(pk=uid)
                
                if default_token_generator.check_token(user, token):
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    return Response({'success': 'Şifreniz başarıyla değiştirildi.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Geçersiz veya süresi dolmuş bağlantı.'}, status=status.HTTP_400_BAD_REQUEST)
                    
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({'error': 'Geçersiz bağlantı.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
