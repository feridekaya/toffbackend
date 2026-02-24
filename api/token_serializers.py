from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    JWT payload'ına ek kullanıcı bilgileri ekler.
    Dönen token decode edildiğinde şu alanlar bulunur:
      - email
      - first_name
      - last_name
      - is_staff
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Özel claim'ler
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_staff'] = user.is_staff

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Response body'ye de kullanıcı bilgisi ekle (frontend kolaylığı)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_staff': self.user.is_staff,
        }
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
