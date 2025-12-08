# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import UserCreateView

# Router oluştur
router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'collections', views.CollectionViewSet, basename='collection')
router.register(r'favorites', views.FavoriteViewSet, basename='favorite')
router.register(r'addresses', views.AddressViewSet, basename='address')
router.register(r'cart', views.CartViewSet, basename='cart')

# URL patterns
urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('user/', views.UserProfileView.as_view(), name='user-profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('coupons/validate/', views.validate_coupon, name='validate-coupon'),
    path('orders/create/', views.create_order, name='create-order'),
    path('', include(router.urls)),
]