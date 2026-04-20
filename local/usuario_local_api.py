from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate

from auth.auth import AuthBearer, require_admin
from local.models import Local, UsuarioLocal
from usuario.models import Usuario


class LocalAsignadoSchema(Schema):
    id: int
    nombre: str


class UsuarioConLocalesSchema(Schema):
    usuario_id: int
    email: str
    es_admin: bool
    locales: list[LocalAsignadoSchema]


class UsuarioLocalPayloadSchema(Schema):
    local_id: int


router = Router(tags=['Usuario Local'])


def _serialize_usuario_locales(usuario: Usuario) -> UsuarioConLocalesSchema:
    relaciones = usuario.locales_asignados.select_related('local').all()
    locales = []
    local_ids = set()

    for relacion in relaciones:
        if relacion.local_id in local_ids:
            continue
        local_ids.add(relacion.local_id)
        locales.append(LocalAsignadoSchema(id=relacion.local.id, nombre=relacion.local.nombre))

    return UsuarioConLocalesSchema(
        usuario_id=usuario.id,
        email=usuario.email,
        es_admin=usuario.es_admin,
        locales=locales,
    )


@router.get('/listar', response=list[UsuarioConLocalesSchema], auth=AuthBearer())
@paginate
def listar_usuarios_con_locales(request):
    base_qs = Usuario.objects.filter(cuenta_id=request.auth.cuenta_id).prefetch_related('locales_asignados__local')

    if request.auth.es_admin:
        usuarios = base_qs.order_by('-id')
    else:
        usuarios = base_qs.filter(id=request.auth.id).order_by('-id')

    return [_serialize_usuario_locales(usuario) for usuario in usuarios]


@router.post('/asignar/{usuario_id}', response=UsuarioConLocalesSchema, auth=AuthBearer())
@require_admin
def asignar_local_a_usuario(request, usuario_id: int, payload: UsuarioLocalPayloadSchema):
    usuario = get_object_or_404(
        Usuario,
        id=usuario_id,
        cuenta_id=request.auth.cuenta_id,
    )
    if usuario.es_admin:
        raise HttpError(400, 'No se puede asignar locales a un usuario admin')

    local = get_object_or_404(
        Local,
        id=payload.local_id,
        cuenta_id=request.auth.cuenta_id,
    )

    UsuarioLocal.objects.get_or_create(usuario=usuario, local=local)

    usuario = Usuario.objects.prefetch_related('locales_asignados__local').get(id=usuario.id)
    return _serialize_usuario_locales(usuario)


@router.post('/desasignar/{usuario_id}', response=UsuarioConLocalesSchema, auth=AuthBearer())
@require_admin
def desasignar_local_a_usuario(request, usuario_id: int, payload: UsuarioLocalPayloadSchema):
    usuario = get_object_or_404(
        Usuario,
        id=usuario_id,
        cuenta_id=request.auth.cuenta_id,
    )
    if usuario.es_admin:
        raise HttpError(400, 'No se puede desasignar locales a un usuario admin')

    local = get_object_or_404(
        Local,
        id=payload.local_id,
        cuenta_id=request.auth.cuenta_id,
    )

    deleted, _ = UsuarioLocal.objects.filter(usuario=usuario, local=local).delete()
    if deleted == 0:
        raise HttpError(404, 'El usuario no tiene asignado ese local')

    usuario = Usuario.objects.prefetch_related('locales_asignados__local').get(id=usuario.id)
    return _serialize_usuario_locales(usuario)
