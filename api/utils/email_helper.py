from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags

def send_toff_email(to_email, subject, context, template_type):
    """
    Sends a branded HTML email.
    
    Args:
        to_email (str): Recipient email address.
        subject (str): Email subject.
        context (dict): Dynamic data for the template.
        template_type (str): 'contact_form', 'password_reset', 'order_shipped',
                             'order_confirmed', 'welcome'
    """
    
    # --- TEMPLATES ---
    
    # Base HTML Wrapper (Dark Luxury)
    def get_html_wrapper(content_body):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ margin: 0; padding: 0; background-color: #1F1F1F; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 40px auto; background-color: #242424; padding: 40px; border-radius: 8px; border: 1px solid #333; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ font-size: 24px; font-weight: bold; color: #EDEDED; letter-spacing: 2px; text-decoration: none; }}
                .content {{ color: #EDEDED; font-size: 16px; line-height: 1.6; }}
                .accent {{ color: #C08B5C; }}
                .button {{ display: inline-block; background-color: #C08B5C; color: #FFFFFF; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; margin-top: 20px; }}
                .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #333; text-align: center; color: #6B7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <span class="logo">TOFF</span>
                </div>
                <div class="content">
                    {content_body}
                </div>
                <div class="footer">
                    <p>Toff Mobilya Tasarım | İstanbul</p>
                    <p>&copy; {2024} TOFF Design. Tüm hakları saklıdır.</p>
                </div>
            </div>
        </body>
        </html>
        """

    # 1. Contact Form (Admin receives this)
    if template_type == 'contact_form':
        # Context needs: name, email, user_subject, message
        body = f"""
        <h2 style="color: #EDEDED; margin-top: 0;">Yeni İletişim Mesajı</h2>
        <p><strong class="accent">Gönderen:</strong> {context.get('name')} ({context.get('email')})</p>
        <p><strong class="accent">Konu:</strong> {context.get('user_subject')}</p>
        <hr style="border: 0; border-top: 1px solid #333; margin: 20px 0;">
        <p style="white-space: pre-line;">{context.get('message')}</p>
        """
        html_content = get_html_wrapper(body)

    # 2. Password Reset (User receives this)
    elif template_type == 'password_reset':
        # Context needs: reset_link
        body = f"""
        <h2 style="color: #EDEDED; margin-top: 0;">Şifrenizi mi unuttunuz?</h2>
        <p>Merhaba,</p>
        <p>Hesabınız için bir şifre sıfırlama talebi aldık. Eğer bu işlemi siz yapmadıysanız bu e-postayı görmezden gelebilirsiniz.</p>
        <p>Şifrenizi yenilemek için aşağıdaki butona tıklayın:</p>
        <div style="text-align: center;">
            <a href="{context.get('reset_link')}" class="button">Şifremi Yenile</a>
        </div>
        <p style="margin-top: 20px; font-size: 14px; color: #9CA3AF;">Link çalışmıyorsa: <br> <a href="{context.get('reset_link')}" style="color: #C08B5C;">{context.get('reset_link')}</a></p>
        """
        html_content = get_html_wrapper(body)

    # 3. Order Shipped (User receives this)
    elif template_type == 'order_shipped':
        # Context needs: full_name, order_id, tracking_number, courier_company (optional)
        body = f"""
        <h2 style="color: #EDEDED; margin-top: 0;">Siparişiniz Yola Çıktı! 🚚</h2>
        <p>Merhaba <span class="accent">{context.get('full_name')}</span>,</p>
        <p>#{context.get('order_id')} numaralı siparişiniz kargoya verildi.</p>
        
        <div style="background-color: #1F1F1F; padding: 15px; border-radius: 4px; border: 1px solid #333; margin: 20px 0;">
            <p style="margin: 5px 0; color: #9CA3AF;">Takip Numarası:</p>
            <p style="margin: 0; font-size: 18px; font-weight: bold; color: #EDEDED;">{context.get('tracking_number')}</p>
        </div>
        
        <div style="text-align: center;">
            <a href="https://tofffrontend-production.up.railway.app/hesabim/siparisler/{context.get('order_id')}" class="button">Kargom Nerede?</a>
        </div>
        """
        html_content = get_html_wrapper(body)
        
    # 4. Sipariş Onayı (Kullanıcıya)
    elif template_type == 'order_confirmed':
        # Context: full_name, order_id, total_amount, items (list of dicts)
        items = context.get('items', [])
        items_html = ''.join([
            f"""
            <tr>
                <td style="padding: 8px 12px; color: #EDEDED; border-bottom: 1px solid #2a2a2a;">
                    {item.get('name')} × {item.get('quantity')}
                    {'<br><small style="color:#9CA3AF">' + item.get('size','') + ' / ' + item.get('color','') + '</small>' if item.get('size') or item.get('color') else ''}
                </td>
                <td style="padding: 8px 12px; color: #C08B5C; text-align: right; border-bottom: 1px solid #2a2a2a;">
                    {float(item.get('price', 0)) * int(item.get('quantity', 1)):,.2f} ₺
                </td>
            </tr>
            """
            for item in items
        ])
        discount_html = ''
        if context.get('discount_amount') and float(context.get('discount_amount', 0)) > 0:
            discount_html = f"""
            <tr>
                <td style="padding: 8px 12px; color: #9CA3AF;">Kupon İndirimi</td>
                <td style="padding: 8px 12px; color: #4ade80; text-align: right;">- {float(context.get('discount_amount', 0)):,.2f} ₺</td>
            </tr>
            """
        body = f"""
        <h2 style="color: #EDEDED; margin-top: 0;">Siparişiniz Alındı! 🎉</h2>
        <p>Merhaba <span class="accent">{context.get('full_name')}</span>,</p>
        <p>#{context.get('order_id')} numaralı siparişiniz başarıyla oluşturuldu. Üretime başladığımızda sizi bilgilendireceğiz.</p>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #1F1F1F; border-radius: 4px;">
            <thead>
                <tr style="background-color: #1a0f05;">
                    <th style="padding: 10px 12px; text-align: left; color: #C08B5C; font-size: 13px;">Ürün</th>
                    <th style="padding: 10px 12px; text-align: right; color: #C08B5C; font-size: 13px;">Toplam</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
                {discount_html}
                <tr style="border-top: 2px solid #333;">
                    <td style="padding: 12px; font-weight: bold; color: #EDEDED;">Genel Toplam</td>
                    <td style="padding: 12px; font-weight: bold; color: #C08B5C; text-align: right;">{float(context.get('total_amount', 0)):,.2f} ₺</td>
                </tr>
            </tbody>
        </table>
        
        <div style="text-align: center;">
            <a href="https://tofffrontend-production.up.railway.app/hesabim/siparisler/{context.get('order_id')}" class="button">Siparişimi Görüntüle</a>
        </div>
        <p style="margin-top: 20px; color: #9CA3AF; font-size: 14px;">Herhangi bir sorunuz için <a href="mailto:thetoffdesign@gmail.com" style="color: #C08B5C;">thetoffdesign@gmail.com</a> adresinden bize ulaşabilirsiniz.</p>
        """
        html_content = get_html_wrapper(body)

    # 5. Hoş Geldin / Kayıt Doğrulama (Kullanıcıya)
    elif template_type == 'welcome':
        # Context: username, email
        body = f"""
        <h2 style="color: #EDEDED; margin-top: 0;">TOFF Ailesine Hoş Geldiniz! 🌟</h2>
        <p>Merhaba <span class="accent">{context.get('username')}</span>,</p>
        <p>Hesabınız başarıyla oluşturuldu. Artık el işçiliğiyle üretilen özel tasarım mobilyalarımıza göz atabilirsiniz.</p>
        
        <div style="background-color: #1F1F1F; padding: 20px; border-radius: 6px; border-left: 3px solid #C08B5C; margin: 20px 0;">
            <p style="margin: 0 0 8px 0; color: #9CA3AF; font-size: 13px;">Kayıtlı E-posta</p>
            <p style="margin: 0; font-weight: bold; color: #EDEDED;">{context.get('email')}</p>
        </div>
        
        <div style="text-align: center;">
            <a href="https://tofffrontend-production.up.railway.app/tum-urunler" class="button">Koleksiyonu Keşfedin</a>
        </div>
        <p style="margin-top: 20px; color: #9CA3AF; font-size: 13px;">
            Siparişlerinizi takip etmek, adres kaydetmek ve faturalarınızı görüntülemek için 
            <a href="https://tofffrontend-production.up.railway.app/hesabim" style="color: #C08B5C;">hesabım</a> sayfanızı kullanabilirsiniz.
        </p>
        """
        html_content = get_html_wrapper(body)

    else:
        raise ValueError("Invalid template type provided")

    # Send Email
    try:
        from django.conf import settings
        import os
        
        # settings.py'de tanımlı değilse doğrudan işletim sistemi ortamından al
        brevo_api_key = getattr(settings, 'BREVO_API_KEY', os.environ.get('BREVO_API_KEY', ''))

        if brevo_api_key:
            # ── Brevo (HTTPS API) Üzerinden Gönderim ──
            # Railway giden port 465 ve 587'yi kapattığı için HTTPS (port 443) üzerinden atıyoruz
            import json
            import urllib.request
            import urllib.error
            url = "https://api.brevo.com/v3/smtp/email"
            data = {
                "sender": {
                    "name": "TOFF Design",
                    "email": settings.DEFAULT_FROM_EMAIL
                },
                "to": [{"email": to_email}],
                "subject": subject,
                "htmlContent": html_content
            }
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'))
            req.add_header('api-key', brevo_api_key)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Accept', 'application/json')
            
            try:
                response = urllib.request.urlopen(req, timeout=10)
                if response.status not in (200, 201, 202):
                    raise Exception(f"Brevo API error: {response.status}")
                return True
            except urllib.error.HTTPError as e:
                # E-posta hatasının JSON detaylarını yakala
                error_body = e.read().decode('utf-8')
                raise Exception(f"Brevo HTTP Hatası ({e.code}): {error_body}")
        
        else:
            # ── Standart SMTP Üzerinden Gönderim (Eski Yöntem) ──
            send_mail(
                subject=subject,
                message=strip_tags(html_content), # Plain text fallback
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=html_content,
                fail_silently=False,
            )
            return True
            
    except Exception as e:
        print(f"Email sending failed: {e}")
        # Hatayı ana view'lara fırlat ki ekranda hatanın ne olduğunu (Örn: API şifresi yanlış) bilelim
        raise e
