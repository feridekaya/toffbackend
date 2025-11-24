# api/iyzico_service.py
"""
Iyzico Payment Gateway Integration
Sandbox (Test) environment configuration
"""

# Iyzico Sandbox API Configuration
IYZICO_OPTIONS = {
    'api_key': 'sandbox-xxxxxxxxxxxxxxxxxxxxxxxx',  # Sandbox API Key
    'secret_key': 'sandbox-yyyyyyyyyyyyyyyyyyyyyyyy',  # Sandbox Secret Key
    'base_url': 'https://sandbox-api.iyzipay.com'  # Test environment
}

def create_payment(cart_items, total_amount, card_info, billing_info):
    """
    Iyzico ile ödeme işlemi gerçekleştirir
    
    Args:
        cart_items: Sepetteki ürünler listesi
        total_amount: Toplam tutar (Decimal)
        card_info: Kart bilgileri dict {
            'card_holder_name': str,
            'card_number': str,
            'expire_month': str,
            'expire_year': str,
            'cvc': str
        }
        billing_info: Fatura bilgileri dict {
            'full_name': str,
            'address': str,
            'city': str,
            'phone': str
        }
    
    Returns:
        dict: {
            'success': bool,
            'payment_id': str (başarılıysa),
            'error_message': str (başarısızsa)
        }
    """
    
    try:
        import iyzipay
        
        # Iyzico Payment Request oluştur
        payment_request = {
            'locale': 'tr',
            'conversationId': f'order_{billing_info.get("phone", "000")}',
            'price': str(total_amount),
            'paidPrice': str(total_amount),
            'currency': 'TRY',
            'installment': '1',
            'basketId': 'B67832',
            'paymentChannel': 'WEB',
            'paymentGroup': 'PRODUCT',
        }
        
        # Kart bilgileri
        payment_card = {
            'cardHolderName': card_info.get('card_holder_name'),
            'cardNumber': card_info.get('card_number'),
            'expireMonth': card_info.get('expire_month'),
            'expireYear': card_info.get('expire_year'),
            'cvc': card_info.get('cvc'),
            'registerCard': '0'
        }
        
        # Alıcı bilgileri
        buyer = {
            'id': 'BY789',
            'name': billing_info.get('full_name', '').split()[0] if billing_info.get('full_name') else 'Ad',
            'surname': ' '.join(billing_info.get('full_name', '').split()[1:]) if len(billing_info.get('full_name', '').split()) > 1 else 'Soyad',
            'gsmNumber': billing_info.get('phone', '+905350000000'),
            'email': 'email@email.com',
            'identityNumber': '74300864791',
            'registrationAddress': billing_info.get('address', 'Adres'),
            'ip': '85.34.78.112',
            'city': billing_info.get('city', 'Istanbul'),
            'country': 'Turkey',
        }
        
        # Adres bilgileri
        shipping_address = {
            'contactName': billing_info.get('full_name', 'Ad Soyad'),
            'city': billing_info.get('city', 'Istanbul'),
            'country': 'Turkey',
            'address': billing_info.get('address', 'Adres'),
        }
        
        billing_address = shipping_address.copy()
        
        # Sepet ürünleri
        basket_items = []
        for item in cart_items:
            basket_items.append({
                'id': str(item['product']['id']),
                'name': item.get('product_name', 'Ürün'),
                'category1': 'Mobilya',
                'itemType': 'PHYSICAL',
                'price': str(float(item.get('price', 0)) * item.get('quantity', 1))
            })
        
        # Tüm parametreleri birleştir
        request = {
            **payment_request,
            'paymentCard': payment_card,
            'buyer': buyer,
            'shippingAddress': shipping_address,
            'billingAddress': billing_address,
            'basketItems': basket_items
        }
        
        # Iyzico Payment API çağrısı
        payment = iyzipay.Payment().create(request, IYZICO_OPTIONS)
        
        # Yanıtı kontrol et
        if payment.read().decode('utf-8'):
            import json
            response = json.loads(payment.read().decode('utf-8'))
            
            if response.get('status') == 'success':
                return {
                    'success': True,
                    'payment_id': response.get('paymentId'),
                    'conversation_id': response.get('conversationId')
                }
            else:
                return {
                    'success': False,
                    'error_message': response.get('errorMessage', 'Ödeme işlemi başarısız oldu.')
                }
        else:
            return {
                'success': False,
                'error_message': 'Ödeme servisi yanıt vermedi.'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error_message': f'Ödeme işlemi sırasında hata oluştu: {str(e)}'
        }


def create_test_payment_success(total_amount):
    """
    Test amaçlı başarılı ödeme simülasyonu
    Gerçek Iyzico entegrasyonu yapılana kadar kullanılabilir
    """
    return {
        'success': True,
        'payment_id': f'TEST_PAYMENT_{total_amount}',
        'conversation_id': 'TEST_CONV_123'
    }


def create_test_payment_failure():
    """
    Test amaçlı başarısız ödeme simülasyonu
    """
    return {
        'success': False,
        'error_message': 'Test: Kart bilgileri geçersiz.'
    }
