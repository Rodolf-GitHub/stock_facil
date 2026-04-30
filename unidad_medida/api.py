from ninja import Router
from ninja.pagination import paginate
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404

from auth.auth import AuthBearer, require_admin
from core.utils.search_filter import search_filter
from unidad_medida.models import UnidadMedida
from unidad_medida.schemas import (
	UnidadMedidaSchema,
	UnidadMedidaCreateSchema,
	UnidadMedidaUpdateSchema,
)

router = Router(tags=['Unidades de Medida'])


@router.get('/listar', response=list[UnidadMedidaSchema], auth=AuthBearer())
@paginate
@search_filter(['nombre'])
def listar_unidades(request):
	return UnidadMedida.objects.filter(cuenta_id=request.auth.cuenta_id).order_by('nombre')


@router.post('/crear', response=UnidadMedidaSchema, auth=AuthBearer())
@require_admin
def crear_unidad(request, payload: UnidadMedidaCreateSchema):
	nombre = payload.nombre.strip()
	if not nombre:
		raise HttpError(400, 'El nombre no puede estar vacio')
	if UnidadMedida.objects.filter(nombre__iexact=nombre, cuenta_id=request.auth.cuenta_id).exists():
		raise HttpError(400, 'Ya existe una unidad de medida con ese nombre')
	return UnidadMedida.objects.create(nombre=nombre, cuenta_id=request.auth.cuenta_id)


@router.put('/actualizar/{unidad_id}', response=UnidadMedidaSchema, auth=AuthBearer())
@require_admin
def actualizar_unidad(request, unidad_id: int, payload: UnidadMedidaUpdateSchema):
	unidad = get_object_or_404(UnidadMedida, id=unidad_id, cuenta_id=request.auth.cuenta_id)
	if payload.nombre is not None:
		nombre = payload.nombre.strip()
		if not nombre:
			raise HttpError(400, 'El nombre no puede estar vacio')
		if UnidadMedida.objects.filter(nombre__iexact=nombre, cuenta_id=request.auth.cuenta_id).exclude(id=unidad_id).exists():
			raise HttpError(400, 'Ya existe una unidad de medida con ese nombre')
		unidad.nombre = nombre
		unidad.save(update_fields=['nombre'])
	return unidad


@router.delete('/eliminar/{unidad_id}', auth=AuthBearer())
@require_admin
def eliminar_unidad(request, unidad_id: int):
	unidad = get_object_or_404(UnidadMedida, id=unidad_id, cuenta_id=request.auth.cuenta_id)
	if unidad.productos.exists():
		raise HttpError(400, 'No se puede eliminar una unidad de medida que tiene productos asociados')
	unidad.delete()
	return {'mensaje': 'Unidad de medida eliminada'}

