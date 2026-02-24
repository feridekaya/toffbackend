from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, help_text="URL için benzersiz kısa isim (örn: yemek-masalari)")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} -> {self.name}"
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Collection(models.Model):
    """Koleksiyonlar - Site yöneticisi tarafından oluşturulan özel ürün grupları"""
    name = models.CharField(max_length=100, help_text="Koleksiyon adı (örn: Bahar 2024, Modern Ofis)")
    slug = models.SlugField(max_length=100, unique=True, help_text="URL için benzersiz kısa isim")
    description = models.TextField(blank=True, null=True, help_text="Koleksiyon açıklaması")
    image = models.ImageField(upload_to='collections/', null=True, blank=True, help_text="Koleksiyon kapak görseli")
    is_active = models.BooleanField(default=True, help_text="Koleksiyon aktif mi?")
    order = models.IntegerField(default=0, help_text="Sıralama (küçükten büyüğe)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Collections"
        ordering = ['order', 'name']


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="İndirimli fiyat (boş bırakılırsa indirim uygulanmaz)")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', help_text="Bu ürünün ait olduğu koleksiyon")
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    stock = models.IntegerField(default=10, help_text="Stok adedi")
    is_active = models.BooleanField(default=True, help_text="Ürün aktif mi? (Pasif ürünler sitede görünmez)")
    material = models.CharField(max_length=200, blank=True, null=True, help_text="Malzeme bilgisi (örn: Meşe, Çelik)")
    dimensions = models.CharField(max_length=200, blank=True, null=True, help_text="Boyutlar (örn: 120x60x75 cm)")
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Ağırlık (kg)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')

    def __str__(self):
        return f"{self.product.name} Image"

class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Bu boyut için geçerli fiyat")

    def __str__(self):
        return f"{self.product.name} - {self.name}"

class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='colors')
    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7, blank=True, null=True, help_text="#RRGGBB formatında renk kodu")

    def __str__(self):
        return f"{self.product.name} - {self.name}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} favorited {self.product.name}"

class Profile(models.Model):
    GENDER_CHOICES = (
        ('female', 'Kadın'),
        ('male', 'Erkek'),
        ('other', 'Diğer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True, null=True, choices=GENDER_CHOICES)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, help_text="Profil fotoğrafı")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

class Address(models.Model):
    BILLING_TYPES = (
        ('individual', 'Bireysel'),
        ('corporate', 'Kurumsal'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=50, help_text="Örn: Evim, İş Yerim")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    neighborhood = models.CharField(max_length=50)
    address_text = models.TextField()
    billing_type = models.CharField(max_length=10, choices=BILLING_TYPES, default='individual')
    tc_id = models.CharField(max_length=11, blank=True, null=True, help_text="Bireysel fatura için TC Kimlik No")
    corporate_name = models.CharField(max_length=100, blank=True, null=True, help_text="Kurumsal fatura için Şirket Adı")
    tax_office = models.CharField(max_length=50, blank=True, null=True, help_text="Kurumsal fatura için Vergi Dairesi")
    tax_number = models.CharField(max_length=20, blank=True, null=True, help_text="Kurumsal fatura için Vergi Numarası")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, help_text="Kupon kodu (örn: YAZ2024)")
    discount_percent = models.IntegerField(help_text="İndirim yüzdesi (örn: 10 için %10)")
    is_active = models.BooleanField(default=True, help_text="Kupon aktif mi?")
    valid_from = models.DateTimeField(help_text="Geçerlilik başlangıç tarihi")
    valid_to = models.DateTimeField(help_text="Geçerlilik bitiş tarihi")
    usage_limit = models.IntegerField(null=True, blank=True, help_text="Toplam kullanım limiti (Boş bırakılırsa limitsiz)")
    used_count = models.IntegerField(default=0, help_text="Kullanılma sayısı")

    def __str__(self):
        return f"{self.code} - %{self.discount_percent}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending_payment', 'Ödeme Bekleniyor'),
        ('order_confirmed', 'Sipariş Onaylandı'),
        ('preparing', 'Üretime Hazırlanıyor'),
        ('metalworks', 'Metal İşçiliği'),
        ('woodworks', 'Ahşap İşçiliği'),
        ('finishing', 'Boya & Vernik'),
        ('quality_control', 'Kalite Kontrol'),
        ('shipped', 'Kargoya Verildi'),
        ('delivered', 'Teslim Edildi'),
        ('cancelled', 'İptal/İade'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    full_name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10, blank=True, null=True, help_text="Posta kodu")
    phone = models.CharField(max_length=15)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', help_text="Kullanılan kupon")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Kupon/indirim tutarı")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    payment_id = models.CharField(max_length=100, blank=True, null=True, help_text="Iyzico ödeme ID")
    customer_note = models.TextField(blank=True, null=True, help_text="Müşteri notu / Özel ölçüler")
    tracking_number = models.CharField(max_length=100, blank=True, null=True, help_text="Kargo takip numarası")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sipariş #{self.id} - {self.full_name}"

    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    selected_size = models.CharField(max_length=50, blank=True, null=True, help_text="Satın alınan boyut (Snapshot)")
    selected_color = models.CharField(max_length=50, blank=True, null=True, help_text="Satın alınan renk (Snapshot)")

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    selected_size = models.ForeignKey(ProductSize, on_delete=models.SET_NULL, null=True, blank=True)
    selected_color = models.ForeignKey(ProductColor, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product', 'selected_size', 'selected_color')

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
