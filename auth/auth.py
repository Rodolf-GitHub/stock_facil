from ninja.security import HttpBearer
from ninja.errors import HttpError
from functools import wraps
from usuario.models import Usuario

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            usuario = Usuario.objects.get(token=(token or '').strip())
            request.usuario = usuario
            return usuario
        except Usuario.DoesNotExist:
            return None


def require_admin(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        usuario = getattr(request, 'auth', None) or getattr(request, 'usuario', None)
        if not usuario or not usuario.es_admin:
            raise HttpError(403, 'Solo administradores pueden realizar esta accion')
        return func(request, *args, **kwargs)

    return wrapper

class GenerateToken:
    @staticmethod
    def generate():
        import uuid
        return str(uuid.uuid4().hex)
