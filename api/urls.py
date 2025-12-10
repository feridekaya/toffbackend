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
router.register(r'orders', views.OrderViewSet, basename='order')

# URL patterns
urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('user/', views.UserProfileView.as_view(), name='user-profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('auth/forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/reset-password-confirm/<uidb64>/<token>/', views.ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
    path('coupons/validate/', views.validate_coupon, name='validate-coupon'),
    path('orders/create/', views.create_order, name='create-order'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('', include(router.urls)),
]