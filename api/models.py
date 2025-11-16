from django.db import models
from django.contrib.auth.models import User
# YENİ: Kategori modelini oluşturuyoruz
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, help_text="URL için benzersiz kısa isim (örn: yemek-masalari)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories" # Admin panelinde "Categorys" yerine "Categories" yazsın


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # YENİ: Ürünü Kategoriye bağlıyoruz
    # ForeignKey = Bir-Çoğa ilişki (Bir kategori, birden çok ürüne sahip olabilir)
    # null=True, blank=True = Kategorisiz ürün olabilir (şimdilik)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    

    # YENİ EKLENEN ALAN
    # 'upload_to' parametresi, resimlerin /media/ klasörünün 
    # içinde 'products/' adlı bir alt klasöre kaydedilmesini sağlar.
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.name
class Favorite(models.Model):
    # Hangi kullanıcıya ait? (User modeline bir 'Yabancı Anahtar')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    
    # Hangi ürüne ait? (Product modeline bir 'Yabancı Anahtar')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    
    # Oluşturulma tarihi (Ne zaman favorilediğini bilelim)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Bir kullanıcının bir ürünü SADECE BİR KEZ favorilemesini sağla
        # (Veritabanı seviyesinde çift kaydı engeller)
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} favorited {self.product.name}"