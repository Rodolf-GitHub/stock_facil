from ninja import Router
from django.contrib.auth.hashers import check_password
from ninja.errors import HttpError
from usuario.models import Usuario
from .auth import GenerateToken
from .schemas import LoginSchema, LoginResponseSchema

router = Router()

@router.post('/login', response=LoginResponseSchema, auth=None)
def login(request, data: LoginSchema):
    try:
        usuario = Usuario.objects.get(email=data.email.strip().lower())
    except Usuario.DoesNotExist:
        raise HttpError(401, 'Credenciales inválidas')

    if not check_password(data.password.strip(), usuario.hash_password):
        raise HttpError(401, 'Credenciales inválidas')

    usuario.token = GenerateToken.generate()
    usuario.save(update_fields=['token'])

    return LoginResponseSchema(
        token=usuario.token,
        usuario_id=usuario.id,
        email=usuario.email,
    )
