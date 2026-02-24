from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAdmin(BasePermission):
    """
    Nesnenin sahibi (obj.user == request.user) veya admin ise izin ver.

    Kullanım:
        permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    Modelin bir 'user' alanı olması gerekir.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        # obj.user veya obj kendisi User ise kontrol et
        owner = getattr(obj, 'user', obj)
        return owner == request.user


class IsAdminOrReadOnly(BasePermission):
    """
    GET/HEAD/OPTIONS → Herkese açık
    POST/PUT/PATCH/DELETE → Sadece admin (is_staff)

    Kullanım:
        permission_classes = [IsAdminOrReadOnly]
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsActiveUser(BasePermission):
    """
    Kullanıcı giriş yapmış VE aktif (is_active=True) olmalı.
    Pasif/banlı hesaplar için kullanılır.

    Kullanım:
        permission_classes = [IsActiveUser]
    """

    message = 'Hesabınız aktif değil. Lütfen destek ile iletişime geçin.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active
        )
