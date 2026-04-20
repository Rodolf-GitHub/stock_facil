from ninja.security import HttpBearer
from usuario.models import Usuario

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            usuario = Usuario.objects.get(token=token)
            return usuario
        except Usuario.DoesNotExist:
            return None

class GenerateToken:
    @staticmethod
    def generate():
        import uuid
        return str(uuid.uuid4().hex)
