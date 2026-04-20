from ninja.security import HttpBearer
from ninja.errors import HttpError
from functools import wraps
import inspect
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

    # Preserve original callable signature so Ninja can still see params
    # added by other decorators (e.g. busqueda from search_filter).
    wrapper.__signature__ = inspect.signature(func)

    return wrapper

class GenerateToken:
    @staticmethod
    def generate():
        import uuid
        return str(uuid.uuid4().hex)
