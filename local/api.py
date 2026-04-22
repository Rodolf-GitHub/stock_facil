from ninja import Router
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

from auth.auth import AuthBearer, require_admin
from core.utils.search_filter import search_filter
from cuenta.models import Cuenta
from local.models import Local
from local.schemas import LocalCreateSchema, LocalSchema, LocalUpdateSchema

router = Router(tags=['Locales'])


@router.get('/listar', response=list[LocalSchema], auth=AuthBearer())
@paginate
@search_filter(['nombre'])
def listar_locales(request):
	if request.auth.es_admin:
		return Local.objects.filter(cuenta_id=request.auth.cuenta_id).order_by('-id')

	return (
		Local.objects.filter(
			cuenta_id=request.auth.cuenta_id,
			usuarios_asignados__usuario_id=request.auth.id,
		)
		.distinct()
		.order_by('-id')
	)


@router.post('/crear', response=LocalSchema, auth=AuthBearer())
@require_admin
def crear_local(request, payload: LocalCreateSchema):
	nombre = payload.nombre.strip()
	if not nombre:
		raise HttpError(400, 'El nombre del local no puede estar vacio')

	cuenta = Cuenta.objects.get(id=request.auth.cuenta_id)
	if Local.objects.filter(cuenta_id=request.auth.cuenta_id).count() >= cuenta.cantidad_maxima_de_locales:
		raise HttpError(400, f'Se alcanzo el limite maximo de {cuenta.cantidad_maxima_de_locales} locales')

	local = Local.objects.create(
		nombre=nombre,
		cuenta_id=request.auth.cuenta_id,
	)
	return local


@router.put('/actualizar/{local_id}', response=LocalSchema, auth=AuthBearer())
@require_admin
def actualizar_local(request, local_id: int, payload: LocalUpdateSchema):
	local = get_object_or_404(
		Local,
		id=local_id,
		cuenta_id=request.auth.cuenta_id,
	)

	update_fields = []
	if payload.nombre is not None:
		nombre = payload.nombre.strip()
		if not nombre:
			raise HttpError(400, 'El nombre del local no puede estar vacio')
		local.nombre = nombre
		update_fields.append('nombre')

	if update_fields:
		local.save(update_fields=update_fields)

	return local


@router.delete('/eliminar/{local_id}', auth=AuthBearer())
@require_admin
def eliminar_local(request, local_id: int):
	local = get_object_or_404(
		Local,
		id=local_id,
		cuenta_id=request.auth.cuenta_id,
	)
	local.delete()
	return {'mensaje': 'Local eliminado'}
