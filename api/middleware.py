import time
import logging
import traceback

from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger('api.requests')
error_logger = logging.getLogger('api.errors')


# ---------------------------------------------------------------------------
# 1. DRF Exception Handler
#    REST_FRAMEWORK['EXCEPTION_HANDLER'] ile kullanılır.
#    Tüm DRF hatalarını tutarlı JSON formatına çevirir.
# ---------------------------------------------------------------------------

def custom_exception_handler(exc, context):
    """
    DRF'nin varsayılan exception handler'ını genişletir.
    Tüm API hatalarını tek tip bir JSON yapısında döner:

    {
        "success": false,
        "error":   "Hata başlığı",
        "detail":  "Detaylı açıklama veya alan hataları",
        "status_code": 400
    }

    settings.py:
        REST_FRAMEWORK = {
            'EXCEPTION_HANDLER': 'api.middleware.custom_exception_handler',
        }
    """
    from rest_framework.views import exception_handler
    from rest_framework.exceptions import (
        ValidationError, AuthenticationFailed, NotAuthenticated,
        PermissionDenied, NotFound, MethodNotAllowed, Throttled,
    )

    # DRF'nin varsayılan işlemcisini önce çalıştır
    response = exception_handler(exc, context)

    # DRF tarafından tanınan bir hata
    if response is not None:
        if isinstance(exc, ValidationError):
            error_title = 'Doğrulama Hatası'
        elif isinstance(exc, NotAuthenticated):
            error_title = 'Kimlik Doğrulama Gerekli'
        elif isinstance(exc, AuthenticationFailed):
            error_title = 'Kimlik Doğrulama Başarısız'
        elif isinstance(exc, PermissionDenied):
            error_title = 'Bu İşlem İçin Yetkiniz Yok'
        elif isinstance(exc, NotFound):
            error_title = 'Kaynak Bulunamadı'
        elif isinstance(exc, MethodNotAllowed):
            error_title = 'HTTP Metodu Desteklenmiyor'
        elif isinstance(exc, Throttled):
            error_title = 'Çok Fazla İstek Gönderildi'
        else:
            error_title = 'API Hatası'

        # Orijinal detail verisini normalize et
        original_detail = response.data
        if isinstance(original_detail, dict) and 'detail' in original_detail:
            detail = str(original_detail['detail'])
        elif isinstance(original_detail, list):
            detail = original_detail
        else:
            detail = original_detail

        response.data = {
            'success': False,
            'error': error_title,
            'detail': detail,
            'status_code': response.status_code,
        }

        if response.status_code >= 500:
            view = context.get('view')
            error_logger.error(
                f"[DRF-500] {exc.__class__.__name__}: {exc} | view: {view}"
            )

        return response

    # DRF tarafından tanınmayan hata → GlobalErrorHandlerMiddleware yakalar
    error_logger.critical(
        f"[UNHANDLED] {exc.__class__.__name__}: {exc}\n{traceback.format_exc()}"
    )
    return None


# ---------------------------------------------------------------------------
# 2. Global Error Handler Middleware
#    Tüm Django isteklerini sarar; DRF dışı hataları (500'ler) da yakalar.
# ---------------------------------------------------------------------------

class GlobalErrorHandlerMiddleware:
    """
    Uygulama genelinde yakalanmamış tüm exception'ları JSON olarak döner.
    /api/ path'lerinde her zaman JSON format kullanır.

    Dönen format:
    {
        "success": false,
        "error":   "Sunucu Hatası",
        "detail":  "...",
        "status_code": 500
    }

    settings.py → MIDDLEWARE listesinin EN BAŞINA ekle:
        'api.middleware.GlobalErrorHandlerMiddleware',
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """Django'nun middleware exception hook'u."""

        # Sadece /api/ path'lerinde JSON dön
        if not request.path.startswith('/api/'):
            return None

        user = getattr(request, 'user', None)
        user_label = (
            (user.email or user.username)
            if user and user.is_authenticated
            else 'anonim'
        )

        error_logger.error(
            f"[GLOBAL-500] {exception.__class__.__name__}: {exception} "
            f"| {request.method} {request.path} "
            f"| kullanıcı: {user_label}\n"
            + traceback.format_exc()
        )

        # DEBUG modunda gerçek hata detayını göster
        if settings.DEBUG:
            detail = f"{exception.__class__.__name__}: {str(exception)}"
        else:
            detail = 'Sunucuda beklenmedik bir hata oluştu. Lütfen daha sonra tekrar deneyin.'

        return JsonResponse(
            {
                'success': False,
                'error': 'Sunucu Hatası',
                'detail': detail,
                'status_code': 500,
            },
            status=500
        )


# ---------------------------------------------------------------------------
# 3. Request Logging Middleware
# ---------------------------------------------------------------------------

class RequestLoggingMiddleware:
    """Her HTTP isteğini loglar: method, path, kullanıcı, status, süre."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        user = getattr(request, 'user', None)
        user_label = (
            (user.email or user.username)
            if user and user.is_authenticated
            else 'anonim'
        )

        log_msg = (
            f"[{request.method}] {request.path} "
            f"| kullanıcı: {user_label} "
            f"| status: {response.status_code} "
            f"| süre: {duration_ms}ms"
        )

        if response.status_code >= 500:
            logger.error(log_msg)
        elif response.status_code >= 400:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        return response


# ---------------------------------------------------------------------------
# 4. JWT Auth Check Middleware
# ---------------------------------------------------------------------------

class JWTAuthCheckMiddleware:
    """Korumalı endpoint'lere tokensiz erişimi loglar."""

    PROTECTED_PREFIXES = (
        '/api/user/', '/api/orders/', '/api/addresses/',
        '/api/favorites/', '/api/cart/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        is_protected = any(request.path.startswith(p) for p in self.PROTECTED_PREFIXES)

        if is_protected:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            user = getattr(request, 'user', None)
            if not auth_header.startswith('Bearer ') and (not user or not user.is_authenticated):
                logger.warning(
                    f"[AUTH] Yetkisiz erişim girişimi: "
                    f"{request.method} {request.path} "
                    f"| IP: {self._get_client_ip(request)}"
                )

        return self.get_response(request)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'bilinmiyor')
