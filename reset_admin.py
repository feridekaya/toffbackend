import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
email = 'admin@example.com'
password = 'password123'
username = 'admin'

try:
    user = User.objects.get(email=email)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"Updated existing user {email} with password {password}")
except User.DoesNotExist:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Created new superuser {email} with password {password}")
