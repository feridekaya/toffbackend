from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags

def send_toff_email(to_email, subject, context, template_type):
    """
    Sends a branded HTML email.
    
    Args:
        to_email (str): Recipient email address.
        subject (str): Email subject.
        context (dict): Dynamic data for the template (e.g., name, detailed_message, tracking_code).
        template_type (str): 'contact_response', 'password_reset', 'order_shipped'
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
        
    else:
        raise ValueError("Invalid template type provided")

    # Send Email
    try:
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
        return False
