from ninja import Router
from ninja.pagination import paginate
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404

from auth.auth import AuthBearer, require_admin
from core.utils.search_filter import search_filter
from local.models import Local, UsuarioLocal
from producto.models import Producto
from plantillastock.models import PlantillaStock
from plantillastock.schemas import (
	PlantillaStockSchema,
	PlantillaStockCreateSchema,
	PlantillaStockUpdateSchema,
)

router = Router(tags=['Plantillas de Stock'])


def _locales_accesibles_ids(usuario):
	if usuario.es_admin:
		return list(
			Local.objects.filter(cuenta_id=usuario.cuenta_id).values_list('id', flat=True)
		)
	return list(
		UsuarioLocal.objects.filter(
			usuario_id=usuario.id,
			local__cuenta_id=usuario.cuenta_id,
		).values_list('local_id', flat=True)
	)


@router.get('/listar', response=list[PlantillaStockSchema], auth=AuthBearer())
@paginate
@search_filter(['producto__nombre'])
def listar_plantillas(request, local_id: int = None):
	locales_ids = _locales_accesibles_ids(request.auth)
	qs = PlantillaStock.objects.filter(local_id__in=locales_ids).select_related('producto')
	if local_id is not None:
		if local_id not in locales_ids:
			raise HttpError(403, 'No tienes acceso a este local')
		qs = qs.filter(local_id=local_id)
	return qs.order_by('-id')


@router.post('/crear', response=PlantillaStockSchema, auth=AuthBearer())
@require_admin
def crear_plantilla(request, payload: PlantillaStockCreateSchema):
	if payload.cantidad_objetivo < 0:
		raise HttpError(400, 'La cantidad objetivo no puede ser negativa')

	local = get_object_or_404(
		Local, id=payload.local_id, cuenta_id=request.auth.cuenta_id
	)
	producto = get_object_or_404(
		Producto, id=payload.producto_id, cuenta_id=request.auth.cuenta_id
	)

	if PlantillaStock.objects.filter(local=local, producto=producto).exists():
		raise HttpError(400, 'Ya existe una plantilla para este producto en el local')

	plantilla = PlantillaStock.objects.create(
		local=local,
		producto=producto,
		cantidad_objetivo=payload.cantidad_objetivo,
	)
	return plantilla


@router.put('/actualizar/{plantilla_id}', response=PlantillaStockSchema, auth=AuthBearer())
@require_admin
def actualizar_plantilla(request, plantilla_id: int, payload: PlantillaStockUpdateSchema):
	plantilla = get_object_or_404(
		PlantillaStock,
		id=plantilla_id,
		local__cuenta_id=request.auth.cuenta_id,
	)

	update_fields = []
	if payload.cantidad_objetivo is not None:
		if payload.cantidad_objetivo < 0:
			raise HttpError(400, 'La cantidad objetivo no puede ser negativa')
		plantilla.cantidad_objetivo = payload.cantidad_objetivo
		update_fields.append('cantidad_objetivo')

	if update_fields:
		plantilla.save(update_fields=update_fields)

	return plantilla


@router.delete('/eliminar/{plantilla_id}', auth=AuthBearer())
@require_admin
def eliminar_plantilla(request, plantilla_id: int):
	plantilla = get_object_or_404(
		PlantillaStock,
		id=plantilla_id,
		local__cuenta_id=request.auth.cuenta_id,
	)
	plantilla.delete()
	return {'mensaje': 'Plantilla eliminada'}
