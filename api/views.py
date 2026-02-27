from rest_framework import viewsets, generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
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


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 24
    page_size_query_param = 'page_size'
    max_page_size = 100


# ---------------------------------------------------------------------------
# PRODUCT
# GET    /api/products/          → Herkese açık (is_active=True, filtreli)
# GET    /api/products/{id}/     → Herkese açık
# POST   /api/products/          → Admin
# PUT    /api/products/{id}/     → Admin
# PATCH  /api/products/{id}/     → Admin
# DELETE /api/products/{id}/     → Admin
# ---------------------------------------------------------------------------

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-id']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        # Admin tüm ürünleri görür; diğerleri sadece aktif ürünleri
        if self.request.user.is_staff:
            queryset = Product.objects.all()
        else:
            queryset = Product.objects.filter(is_active=True)

        # 1. Kategori Filtresi
        category_slug = self.request.query_params.get('category_slug')
        if category_slug:
            if category_slug == 'tum-urunler':
                pass
            elif category_slug == 'yeni-gelenler':
                queryset = queryset.order_by('-created_at')
            else:
                try:
                    category = Category.objects.get(slug=category_slug)

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

        # 3. Slug Filtresi (ürün detay sayfası için)
        product_slug = self.request.query_params.get('slug')
        if product_slug:
            queryset = queryset.filter(slug=product_slug)

        # 4. Arama Filtresi
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        # 5. is_active Filtresi (admin için)
        is_active = self.request.query_params.get('is_active')
        if is_active is not None and self.request.user.is_staff:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset.order_by('-id')


# ---------------------------------------------------------------------------
# CATEGORY
# GET    /api/categories/        → Herkese açık
# GET    /api/categories/{slug}/ → Herkese açık
# POST   /api/categories/        → Admin
# PUT    /api/categories/{slug}/ → Admin
# DELETE /api/categories/{slug}/ → Admin
# ---------------------------------------------------------------------------

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    pagination_class = None

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


# ---------------------------------------------------------------------------
# COLLECTION
# GET    /api/collections/        → Herkese açık (sadece aktif)
# GET    /api/collections/{slug}/ → Herkese açık
# POST   /api/collections/        → Admin
# PUT    /api/collections/{slug}/ → Admin
# DELETE /api/collections/{slug}/ → Admin
# ---------------------------------------------------------------------------

class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'products']:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Collection.objects.all().order_by('order', 'name')
        return Collection.objects.filter(is_active=True).order_by('order', 'name')

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """GET /api/collections/{slug}/products/"""
        collection = self.get_object()
        products = collection.products.filter(is_active=True)

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(products, request)
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# USER
# POST   /api/register/          → Herkese açık
# GET    /api/user/              → Auth
# PUT    /api/user/              → Auth
# DELETE /api/user/              → Auth (kendi hesabını sil)
# GET    /api/users/             → Admin (kullanıcı listesi)
# ---------------------------------------------------------------------------

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        
        # ── Hoş Geldin Emaili (Kayıt Sonrası) ─────────────────────────
        try:
            from .utils.email_helper import send_toff_email
            send_toff_email(
                to_email=user.email,
                subject="TOFF Ailesine Hoş Geldiniz! 🌟",
                context={
                    'username': user.username,
                    'email':    user.email,
                },
                template_type='welcome',
            )
        except Exception as e:
            print(f"Hoşgeldin email hatası: {e}")



class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/user/ → Profil getir
    PUT    /api/user/ → Profil güncelle
    PATCH  /api/user/ → Kısmi güncelle
    DELETE /api/user/ → Hesabı kalıcı olarak sil
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response(
            {'detail': 'Hesabınız başarıyla silindi.'},
            status=status.HTTP_204_NO_CONTENT
        )


class UserListView(generics.ListAPIView):
    """
    GET /api/users/ → Admin: Tüm kullanıcıları listele
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination


# ---------------------------------------------------------------------------
# CHANGE PASSWORD
# PUT /api/change-password/ → Auth
# ---------------------------------------------------------------------------

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Eski şifre yanlış."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"detail": "Şifre başarıyla güncellendi."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# FAVORITE
# GET    /api/favorites/      → Auth (kendi favorileri)
# POST   /api/favorites/      → Auth
# DELETE /api/favorites/{id}/ → Auth
# ---------------------------------------------------------------------------

class FavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FavoriteReadSerializer
        return FavoriteWriteSerializer

    def get_queryset(self):
        from .models import Favorite
        return Favorite.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------------------------------------------------------------------
# ADDRESS
# GET    /api/addresses/      → Auth (kendi adresleri)
# POST   /api/addresses/      → Auth
# PUT    /api/addresses/{id}/ → Auth
# DELETE /api/addresses/{id}/ → Auth
# ---------------------------------------------------------------------------

class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------------------------------------------------------------------
# COUPON
# GET    /api/coupons/          → Admin
# POST   /api/coupons/          → Admin
# PUT    /api/coupons/{id}/     → Admin
# DELETE /api/coupons/{id}/     → Admin
# POST   /api/coupons/validate/ → Herkese açık
# ---------------------------------------------------------------------------

class CouponViewSet(viewsets.ModelViewSet):
    """Admin için tam kupon yönetimi."""
    queryset = Coupon.objects.all().order_by('-id')
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_coupon(request):
    """POST /api/coupons/validate/ → Kupon kodu doğrula"""
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

    return Response({
        'code': coupon.code,
        'discount_percent': coupon.discount_percent,
        'valid_until': coupon.valid_to,
    })


# ---------------------------------------------------------------------------
# ORDER
# GET    /api/orders/                    → Auth (kendi), Admin (hepsi)
# GET    /api/orders/{id}/               → Auth (kendi), Admin
# PATCH  /api/orders/{id}/update_status/ → Admin
# DELETE /api/orders/{id}/               → Admin
# POST   /api/orders/create/             → Herkese açık (kupon destekli)
# ---------------------------------------------------------------------------

class OrderViewSet(viewsets.ModelViewSet):
    """
    Kullanıcılar sadece kendi siparişlerini görür (list/retrieve).
    Admin tüm siparişleri yönetebilir.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        PATCH /api/orders/{id}/update_status/
        Body: { "status": "preparing", "tracking_number": "TRK123" }
        """
        if not request.user.is_staff:
            return Response({'error': 'Yetkiniz yok.'}, status=status.HTTP_403_FORBIDDEN)

        order = self.get_object()
        new_status = request.data.get('status')
        tracking_number = request.data.get('tracking_number')

        if new_status:
            valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
            if new_status not in valid_statuses:
                return Response(
                    {'error': f'Geçersiz durum. Geçerli değerler: {valid_statuses}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            order.status = new_status

            # Kargoya verildi → email gönder
            if new_status == 'shipped' and order.user and order.user.email:
                try:
                    from .utils.email_helper import send_toff_email
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
                except Exception:
                    pass  # Email hatası siparişi durdurmasın

        if tracking_number is not None:
            order.tracking_number = tracking_number

        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_order(request):
    """
    POST /api/orders/create/
    Sipariş oluşturur. Kupon kodu varsa indirim uygular.
    """
    full_name = request.data.get('full_name')
    address = request.data.get('address')
    city = request.data.get('city')
    zip_code = request.data.get('zip_code', '')
    phone = request.data.get('phone')
    cart_items = request.data.get('cart_items', [])
    coupon_code = request.data.get('coupon_code', None)
    customer_note = request.data.get('customer_note', '')
    card_info = request.data.get('card_info', {})

    # Zorunlu alan kontrolü
    if not all([full_name, address, city, phone]):
        return Response(
            {'error': 'Lütfen tüm teslimat bilgilerini doldurunuz.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not cart_items:
        return Response({'error': 'Sepetiniz boş.'}, status=status.HTTP_400_BAD_REQUEST)

    # 1. STOK KONTROLÜ
    out_of_stock_products = []
    total_amount = 0

    for item in cart_items:
        product_id = item.get('product', {}).get('id')
        quantity = item.get('quantity', 0)

        try:
            product = Product.objects.get(id=product_id)

            if product.stock < quantity:
                out_of_stock_products.append({
                    'product': product.name,
                    'requested': quantity,
                    'available': product.stock
                })

            # İndirimli fiyat varsa onu kullan
            unit_price = float(product.discount_price or product.price)
            total_amount += unit_price * quantity

        except Product.DoesNotExist:
            return Response(
                {'error': f'Ürün bulunamadı: ID {product_id}'},
                status=status.HTTP_404_NOT_FOUND
            )

    if out_of_stock_products:
        return Response(
            {'error': 'Bazı ürünlerin stoğu yetersiz.', 'out_of_stock': out_of_stock_products},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 2. KUPON DOĞRULAMA VE İNDİRİM HESAPLAMA
    coupon = None
    discount_amount = 0

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code.upper())
            now = timezone.now()

            if (
                coupon.is_active and
                coupon.valid_from <= now <= coupon.valid_to and
                (coupon.usage_limit is None or coupon.used_count < coupon.usage_limit)
            ):
                discount_amount = total_amount * (coupon.discount_percent / 100)
                total_amount -= discount_amount
            else:
                return Response(
                    {'error': 'Kupon geçersiz veya süresi dolmuş.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Coupon.DoesNotExist:
            return Response({'error': 'Geçersiz kupon kodu.'}, status=status.HTTP_400_BAD_REQUEST)

    # 3. ÖDEME İŞLEMİ (Iyzico)
    payment_result = iyzico_service.create_test_payment_success(total_amount)

    if not payment_result.get('success'):
        return Response(
            {'error': 'Ödeme işlemi başarısız oldu.', 'detail': payment_result.get('error_message')},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 4. SİPARİŞ KAYDI
    try:
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=full_name,
                address=address,
                city=city,
                zip_code=zip_code,
                phone=phone,
                total_amount=total_amount,
                coupon=coupon,
                discount_amount=discount_amount,
                status='order_confirmed',
                payment_id=payment_result.get('payment_id'),
                customer_note=customer_note,
            )

            for item in cart_items:
                product_id = item.get('product', {}).get('id')
                quantity = item.get('quantity', 0)

                selected_size_obj = item.get('selectedSize') or item.get('selected_size')
                selected_color_obj = item.get('selectedColor') or item.get('selected_color')
                size_name = selected_size_obj.get('name') if selected_size_obj else None
                color_name = selected_color_obj.get('name') if selected_color_obj else None

                product = Product.objects.select_for_update().get(id=product_id)
                unit_price = float(product.discount_price or product.price)

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    quantity=quantity,
                    price=unit_price,
                    selected_size=size_name,
                    selected_color=color_name,
                )

                product.stock -= quantity
                product.save()

            # Kupon kullanım sayısını artır
            if coupon:
                coupon.used_count += 1
                coupon.save()

            # ── Sipariş Onayı Emaili ──────────────────────────────
            try:
                from .utils.email_helper import send_toff_email
                recipient_email = (
                    request.user.email
                    if request.user.is_authenticated
                    else None
                )
                if recipient_email:
                    email_items = [
                        {
                            'name':     oi.product_name,
                            'quantity': oi.quantity,
                            'price':    float(oi.price),
                            'size':     oi.selected_size  or '',
                            'color':    oi.selected_color or '',
                        }
                        for oi in order.items.all()
                    ]
                    send_toff_email(
                        to_email=recipient_email,
                        subject=f"Siparişiniz Alındı #{order.id} — TOFF Design",
                        context={
                            'full_name':       order.full_name,
                            'order_id':        order.id,
                            'items':           email_items,
                            'discount_amount': round(discount_amount, 2),
                            'total_amount':    round(total_amount, 2),
                        },
                        template_type='order_confirmed',
                    )
            except Exception as email_err:
                print(f"Sipariş email hatası: {email_err}")  # Loglama — siparişi durdurma

            return Response({
                'success': True,
                'message': 'Siparişiniz başarıyla alındı!',
                'order_id': order.id,
                'payment_id': payment_result.get('payment_id'),
                'discount_amount': round(discount_amount, 2),
                'total_amount': round(total_amount, 2),
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': 'Sipariş oluşturulurken bir hata oluştu.', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ---------------------------------------------------------------------------
# CART
# GET  /api/cart/                  → Auth
# POST /api/cart/add_item/         → Auth
# POST /api/cart/remove_item/      → Auth
# POST /api/cart/update_quantity/  → Auth
# ---------------------------------------------------------------------------

from .models import Cart, CartItem, ProductSize, ProductColor
from .serializers import CartSerializer, CartItemSerializer


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)

        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        size_id = request.data.get('selected_size_id')
        color_id = request.data.get('selected_color_id')

        if not product_id:
            return Response({'error': 'product_id gereklidir.'}, status=400)

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'error': 'Ürün bulunamadı.'}, status=404)

        size = ProductSize.objects.get(id=size_id) if size_id else None
        color = ProductColor.objects.get(id=color_id) if color_id else None

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

        return Response(self.get_serializer(cart).data)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item_id = request.data.get('item_id')

        if not item_id:
            return Response({'error': 'item_id gereklidir.'}, status=400)

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
            item.delete()
        except CartItem.DoesNotExist:
            return Response({'error': 'Sepet ürünü bulunamadı.'}, status=404)

        return Response(self.get_serializer(cart).data)

    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))

        if not item_id:
            return Response({'error': 'item_id gereklidir.'}, status=400)

        if quantity < 1:
            return Response({'error': 'Miktar en az 1 olmalıdır.'}, status=400)

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
            item.quantity = quantity
            item.save()
        except CartItem.DoesNotExist:
            return Response({'error': 'Sepet ürünü bulunamadı.'}, status=404)

        return Response(self.get_serializer(cart).data)


# ---------------------------------------------------------------------------
# CONTACT FORM
# POST /api/contact/ → Herkese açık
# ---------------------------------------------------------------------------

from .utils.email_helper import send_toff_email


class ContactView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        subject = request.data.get('subject')
        message = request.data.get('message')

        if not all([name, email, subject, message]):
            return Response(
                {'error': 'Lütfen tüm alanları doldurunuz.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        email_sent = send_toff_email(
            to_email='thetoffdesign@gmail.com',
            subject=f"TOFF İletişim: {subject} - {name}",
            context={'name': name, 'email': email, 'user_subject': subject, 'message': message},
            template_type='contact_form'
        )

        if email_sent:
            return Response({'success': True, 'message': 'Mesajınız iletildi.'})
        return Response(
            {'error': 'Mesaj gönderilemedi. Lütfen daha sonra tekrar deneyiniz.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ---------------------------------------------------------------------------
# PASSWORD RESET
# POST /api/auth/forgot-password/                         → Herkese açık
# POST /api/auth/reset-password-confirm/{uid}/{token}/    → Herkese açık
# ---------------------------------------------------------------------------

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .serializers import ForgotPasswordSerializer, ResetPasswordSerializer

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
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = f"{FRONTEND_URL}/reset-password?uid={uid}&token={token}"
                send_toff_email(
                    to_email=user.email,
                    subject="Şifrenizi mi unuttunuz?",
                    context={'reset_link': reset_link},
                    template_type='password_reset'
                )
                
                return Response(
                    {'success': 'Şifre sıfırlama bağlantısı e-posta adresinize gönderildi.'},
                    status=status.HTTP_200_OK
                )
            except User.DoesNotExist:
                # Kullanıcı yoksa hata ver
                return Response(
                    {'error': 'Bu e-posta adresiyle kayıtlı bir hesap bulunamadı.'},
                    status=status.HTTP_404_NOT_FOUND
                )

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
                    return Response(
                        {'success': 'Şifreniz başarıyla değiştirildi.'},
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {'error': 'Geçersiz veya süresi dolmuş bağlantı.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({'error': 'Geçersiz bağlantı.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
