# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products',    views.ProductViewSet,    basename='product')
router.register(r'categories',  views.CategoryViewSet,   basename='category')
router.register(r'collections', views.CollectionViewSet, basename='collection')
router.register(r'favorites',   views.FavoriteViewSet,   basename='favorite')
router.register(r'addresses',   views.AddressViewSet,    basename='address')
router.register(r'cart',        views.CartViewSet,       basename='cart')
router.register(r'orders',      views.OrderViewSet,      basename='order')
router.register(r'coupons',     views.CouponViewSet,     basename='coupon')

urlpatterns = [
    # --- Auth & User ---
    path('register/',           views.UserCreateView.as_view(),          name='user-register'),
    path('user/',               views.UserProfileView.as_view(),         name='user-profile'),       # GET / PUT / PATCH / DELETE
    path('users/',              views.UserListView.as_view(),             name='user-list'),           # GET (admin)
    path('change-password/',    views.ChangePasswordView.as_view(),       name='change-password'),     # PUT

    # --- Password Reset ---
    path('auth/forgot-password/',                                   views.ForgotPasswordView.as_view(),        name='forgot-password'),
    path('auth/reset-password-confirm/<uidb64>/<token>/',           views.ResetPasswordConfirmView.as_view(),  name='reset-password-confirm'),

    # --- Coupon ---
    path('coupons/validate/',   views.validate_coupon,               name='validate-coupon'),         # POST (public)

    # --- Order ---
    path('orders/create/',      views.create_order,                  name='create-order'),            # POST (public, kupon destekli)

    # --- Contact ---
    path('contact/',            views.ContactView.as_view(),          name='contact'),                 # POST

    # --- Router ---
    path('', include(router.urls)),
]