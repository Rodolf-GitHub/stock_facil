from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import paginate

from auth.auth import AuthBearer, require_admin
from core.utils.search_filter import search_filter
from cuenta.models import Cuenta
from usuario.models import Usuario
from usuario.schemas import (
    UsuarioCambiarMiContrasenaSchema,
    UsuarioCreateSchema,
    UsuarioRestablecerContrasenaSchema,
    UsuarioSchema,
)

router = Router(tags=['Usuarios'])


@router.get('/listar', response=list[UsuarioSchema], auth=AuthBearer())
@require_admin
@paginate
@search_filter(['email'])
def listar_usuarios(request):
    return Usuario.objects.filter(cuenta_id=request.auth.cuenta_id).order_by('-id')


@router.post('/crear', response=UsuarioSchema, auth=AuthBearer())
@require_admin
def crear_usuario(request, payload: UsuarioCreateSchema):
    email = payload.email.strip().lower()
    raw_password = payload.password.strip()

    if Usuario.objects.filter(email=email).exists():
        raise HttpError(400, 'El email ya esta registrado')

    cuenta = Cuenta.objects.get(id=request.auth.cuenta_id)
    if Usuario.objects.filter(cuenta_id=request.auth.cuenta_id).count() >= cuenta.cantidad_maxima_de_usuarios:
        raise HttpError(400, f'Se alcanzo el limite maximo de {cuenta.cantidad_maxima_de_usuarios} usuarios')

    usuario = Usuario.objects.create(
        cuenta_id=request.auth.cuenta_id,
        email=email,
        hash_password=make_password(raw_password),
    )
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


@router.put('/restablecer_contrasena/{usuario_id}', response=UsuarioSchema, auth=AuthBearer())
@require_admin
def restablecer_contrasena_usuario(request, usuario_id: int, payload: UsuarioRestablecerContrasenaSchema):
    nueva_password = payload.nueva_password.strip()
    if not nueva_password:
        raise HttpError(400, 'La nueva contrasena no puede estar vacia')

    usuario = get_object_or_404(
        Usuario,
        id=usuario_id,
        cuenta_id=request.auth.cuenta_id,
    )
    usuario.hash_password = make_password(nueva_password)
    usuario.save(update_fields=['hash_password'])
    return usuario


@router.put('/cambiar_mi_contrasena', response=UsuarioSchema, auth=AuthBearer())
def cambiar_mi_contrasena(request, payload: UsuarioCambiarMiContrasenaSchema):
    password_actual = payload.password_actual.strip()
    nueva_password = payload.nueva_password.strip()

    if not password_actual or not nueva_password:
        raise HttpError(400, 'La contrasena actual y la nueva son obligatorias')

    usuario = request.auth
    if not check_password(password_actual, usuario.hash_password):
        raise HttpError(400, 'La contrasena actual es incorrecta')

    usuario.hash_password = make_password(nueva_password)
    usuario.save(update_fields=['hash_password'])
    return usuario
