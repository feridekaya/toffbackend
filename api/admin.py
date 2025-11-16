# api/admin.py
from django.contrib import admin
from .models import Product, Category, Favorite

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'slug')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # HATA BURADAYDI: 'parent' alanını list_display'den çıkarıyoruz
    list_display = ('name', 'slug') 
    prepopulated_fields = {'slug': ('name',)}
    
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('user', 'created_at')