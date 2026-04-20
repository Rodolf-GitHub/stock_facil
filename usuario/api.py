from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import paginate

from auth.auth import AuthBearer, require_admin
from core.utils.search_filter import search_filter
from usuario.models import Usuario
from usuario.schemas import UsuarioCreateSchema, UsuarioSchema, UsuarioUpdateSchema

router = Router(tags=['Usuarios'])


@router.get('/listar', response=list[UsuarioSchema], auth=AuthBearer())
@require_admin
@paginate
@search_filter(['email'])
def listar_usuarios(request, busqueda: str = None):
    return Usuario.objects.filter(cuenta_id=request.auth.cuenta_id).order_by('-id')


@router.post('/crear', response=UsuarioSchema, auth=AuthBearer())
@require_admin
def crear_usuario(request, payload: UsuarioCreateSchema):
    email = payload.email.strip().lower()
    raw_password = payload.password.strip()

    if Usuario.objects.filter(email=email).exists():
        raise HttpError(400, 'El email ya esta registrado')

    usuario = Usuario.objects.create(
        cuenta_id=request.auth.cuenta_id,
        email=email,
        hash_password=make_password(raw_password),
    )
    return usuario


@router.put('/actualizar/{usuario_id}', response=UsuarioSchema, auth=AuthBearer())
@require_admin
def actualizar_usuario(request, usuario_id: int, payload: UsuarioUpdateSchema):
    usuario = get_object_or_404(
        Usuario,
        id=usuario_id,
        cuenta_id=request.auth.cuenta_id,
    )

    update_fields = []

    if payload.email is not None:
        email = payload.email.strip().lower()
        if Usuario.objects.filter(email=email).exclude(id=usuario.id).exists():
            raise HttpError(400, 'El email ya esta registrado')
        usuario.email = email
        update_fields.append('email')

    if payload.password is not None:
        usuario.hash_password = make_password(payload.password.strip())
        update_fields.append('hash_password')

    if update_fields:
        usuario.save(update_fields=update_fields)

    return usuario


@router.delete('/eliminar/{usuario_id}', auth=AuthBearer())
@require_admin
def eliminar_usuario(request, usuario_id: int):
    usuario = get_object_or_404(
        Usuario,
        id=usuario_id,
        cuenta_id=request.auth.cuenta_id,
    )
    usuario.delete()
    return {'mensaje': 'Usuario eliminado'}
