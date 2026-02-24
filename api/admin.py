from django.contrib import admin
from .models import Product, Category, Collection, Favorite, Profile, Address, ProductImage, ProductSize, ProductColor, Coupon, Order, OrderItem

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'collection', 'price', 'discount_price', 'stock', 'is_active', 'slug', 'created_at')
    list_filter = ('category', 'collection', 'is_active')
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'material')
    inlines = [ProductImageInline, ProductSizeInline, ProductColorInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    list_filter = ('parent',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'order')
    search_fields = ('name', 'description')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('user', 'created_at')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'city', 'district', 'billing_type', 'created_at')
    list_filter = ('billing_type', 'city', 'created_at')
    search_fields = ('title', 'user__username', 'first_name', 'last_name', 'city')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'is_active', 'valid_from', 'valid_to', 'usage_limit', 'used_count')
    list_filter = ('is_active', 'valid_from', 'valid_to')
    search_fields = ('code',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'quantity', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'city', 'total_amount', 'discount_amount', 'coupon', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'phone', 'payment_id')
    readonly_fields = ('payment_id', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

admin.site.register(Profile)