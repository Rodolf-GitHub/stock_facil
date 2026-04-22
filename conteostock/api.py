from datetime import date as date_type
from collections import defaultdict
from decimal import Decimal

from ninja import Router
from ninja.pagination import paginate
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.utils import timezone

from auth.auth import AuthBearer
from local.models import Local, UsuarioLocal
from plantillastock.models import PlantillaStock
from cuenta.models import Cuenta
from conteostock.models import ConteoStock, ItemConteoStock
from conteostock.schemas import (
	ConteoStockSchema,
	ConteoStockCreateSchema,
	ConteoStockUpdateSchema,
	ItemConteoStockSchema,
	ItemConteoStockCreateSchema,
	ItemConteoStockUpdateSchema,
	ListaCompraLocalSchema,
	ItemListaCompraSchema,
	ItemListaCompraTotalSchema,
	ListaCompraTotalSchema,
	LocalSinConteoSchema,
	ResumenConteoSchema,
	ResumenLocalFechaSchema,
)

router = Router(tags=['Conteos de Stock'])


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


def _verificar_acceso_local(usuario, local_id):
	if local_id not in _locales_accesibles_ids(usuario):
		raise HttpError(403, 'No tienes acceso a este local')


# ---------------- ConteoStock ----------------

@router.get('/listar', response=list[ConteoStockSchema], auth=AuthBearer())
@paginate
def listar_conteos(request, local_id: int = None, fecha: date_type = None):
	locales_ids = _locales_accesibles_ids(request.auth)
	qs = ConteoStock.objects.filter(local_id__in=locales_ids)
	if local_id is not None:
		_verificar_acceso_local(request.auth, local_id)
		qs = qs.filter(local_id=local_id)
	if fecha is not None:
		qs = qs.filter(fecha=fecha)
	return qs.order_by('-fecha', '-id')


@router.get('/obtener/{conteo_id}', response=ConteoStockSchema, auth=AuthBearer())
def obtener_conteo(request, conteo_id: int):
	conteo = get_object_or_404(
		ConteoStock,
		id=conteo_id,
		local__cuenta_id=request.auth.cuenta_id,
	)
	_verificar_acceso_local(request.auth, conteo.local_id)
	return conteo


@router.post('/crear', response=ConteoStockSchema, auth=AuthBearer())
def crear_conteo(request, payload: ConteoStockCreateSchema):
	local = get_object_or_404(
		Local, id=payload.local_id, cuenta_id=request.auth.cuenta_id
	)
	_verificar_acceso_local(request.auth, local.id)

	fecha = payload.fecha or timezone.now().date()

	if ConteoStock.objects.filter(local=local, fecha=fecha).exists():
		raise HttpError(400, 'Ya existe un conteo para este local en esta fecha')

	cuenta = Cuenta.objects.get(id=request.auth.cuenta_id)
	cantidad_actual = ConteoStock.objects.filter(local__cuenta_id=request.auth.cuenta_id).count()
	if cantidad_actual >= cuenta.cantidad_maxima_de_conteo_stock:
		cantidad_a_eliminar = max(1, cuenta.cantidad_maxima_de_conteo_stock // 10)
		ids_a_eliminar = list(
			ConteoStock.objects.filter(local__cuenta_id=request.auth.cuenta_id)
			.order_by('fecha', 'id')
			.values_list('id', flat=True)[:cantidad_a_eliminar]
		)
		ConteoStock.objects.filter(id__in=ids_a_eliminar).delete()

	conteo = ConteoStock.objects.create(
		local=local,
		fecha=fecha,
		creado_por=request.auth,
	)
	return conteo


@router.put('/actualizar/{conteo_id}', response=ConteoStockSchema, auth=AuthBearer())
def actualizar_conteo(request, conteo_id: int, payload: ConteoStockUpdateSchema):
	conteo = get_object_or_404(
		ConteoStock,
		id=conteo_id,
		local__cuenta_id=request.auth.cuenta_id,
	)
	_verificar_acceso_local(request.auth, conteo.local_id)

	if conteo.estado == ConteoStock.ESTADO_FINALIZADO:
		raise HttpError(400, 'No se puede modificar un conteo finalizado')

	update_fields = []
	if payload.fecha is not None:
		if ConteoStock.objects.filter(
			local_id=conteo.local_id, fecha=payload.fecha
		).exclude(id=conteo.id).exists():
			raise HttpError(400, 'Ya existe un conteo para este local en esta fecha')
		conteo.fecha = payload.fecha
		update_fields.append('fecha')

	if update_fields:
		conteo.save(update_fields=update_fields)

	return conteo


@router.post('/finalizar/{conteo_id}', response=ConteoStockSchema, auth=AuthBearer())
def finalizar_conteo(request, conteo_id: int):
	conteo = get_object_or_404(
		ConteoStock,
		id=conteo_id,
		local__cuenta_id=request.auth.cuenta_id,
	)
	_verificar_acceso_local(request.auth, conteo.local_id)

	if conteo.estado == ConteoStock.ESTADO_FINALIZADO:
		raise HttpError(400, 'El conteo ya esta finalizado')

	productos_plantilla = set(
		PlantillaStock.objects.filter(local_id=conteo.local_id).values_list(
			'producto_id', flat=True
		)
	)
	if not productos_plantilla:
		raise HttpError(400, 'El local no tiene productos en plantilla')

	productos_conteo = set(
		ItemConteoStock.objects.filter(conteo_stock=conteo).values_list(
			'producto_id', flat=True
		)
	)
	faltantes = productos_plantilla - productos_conteo
	if faltantes:
		raise HttpError(
			400,
			f'Faltan items para los productos: {sorted(faltantes)}',
		)

	conteo.estado = ConteoStock.ESTADO_FINALIZADO
	conteo.save(update_fields=['estado'])
	return conteo


@router.post('/reabrir/{conteo_id}', response=ConteoStockSchema, auth=AuthBearer())
def reabrir_conteo(request, conteo_id: int):
	conteo = get_object_or_404(
		ConteoStock,
		id=conteo_id,
		local__cuenta_id=request.auth.cuenta_id,
	)
	_verificar_acceso_local(request.auth, conteo.local_id)

	if conteo.estado != ConteoStock.ESTADO_FINALIZADO:
		raise HttpError(400, 'El conteo no esta finalizado')

	conteo.estado = ConteoStock.ESTADO_BORRADOR
	conteo.save(update_fields=['estado'])
	return conteo


@router.delete('/eliminar/{conteo_id}', auth=AuthBearer())
def eliminar_conteo(request, conteo_id: int):
	conteo = get_object_or_404(
		ConteoStock,
		id=conteo_id,
		local__cuenta_id=request.auth.cuenta_id,
	)
	_verificar_acceso_local(request.auth, conteo.local_id)
	conteo.delete()
	return {'mensaje': 'Conteo eliminado'}


# ---------------- Items ----------------

@router.get('/items/listar/{conteo_id}', response=list[ItemConteoStockSchema], auth=AuthBearer())
def listar_items(request, conteo_id: int):
	conteo = get_object_or_404(
		ConteoStock,
		id=conteo_id,
		local__cuenta_id=request.auth.cuenta_id,
	)
	_verificar_acceso_local(request.auth, conteo.local_id)
	return ItemConteoStock.objects.filter(conteo_stock=conteo).order_by('id')


@router.post('/items/crear', response=ItemConteoStockSchema, auth=AuthBearer())
def crear_item(request, payload: ItemConteoStockCreateSchema):
	if payload.cantidad_conteada < 0:
		raise HttpError(400, 'La cantidad conteada no puede ser negativa')

	conteo = get_object_or_404(
		ConteoStock,
		id=payload.conteo_stock_id,
		local__cuenta_id=request.auth.cuenta_id,
	)
	_verificar_acceso_local(request.auth, conteo.local_id)

	if conteo.estado == ConteoStock.ESTADO_FINALIZADO:
		raise HttpError(400, 'No se puede modificar un conteo finalizado')

	if not PlantillaStock.objects.filter(
		local_id=conteo.local_id, producto_id=payload.producto_id
	).exists():
		raise HttpError(400, 'El producto no esta en la plantilla del local')

	if ItemConteoStock.objects.filter(
		conteo_stock=conteo, producto_id=payload.producto_id
	).exists():
		raise HttpError(400, 'Ya existe un item para este producto en el conteo')

	item = ItemConteoStock.objects.create(
		conteo_stock=conteo,
		producto_id=payload.producto_id,
		cantidad_conteada=payload.cantidad_conteada,
	)
	return item


@router.put('/items/actualizar/{item_id}', response=ItemConteoStockSchema, auth=AuthBearer())
def actualizar_item(request, item_id: int, payload: ItemConteoStockUpdateSchema):
	item = get_object_or_404(
		ItemConteoStock,
		id=item_id,
		conteo_stock__local__cuenta_id=request.auth.cuenta_id,
	)
	_verificar_acceso_local(request.auth, item.conteo_stock.local_id)

	if item.conteo_stock.estado == ConteoStock.ESTADO_FINALIZADO:
		raise HttpError(400, 'No se puede modificar un conteo finalizado')

	update_fields = []
	if payload.cantidad_conteada is not None:
		if payload.cantidad_conteada < 0:
			raise HttpError(400, 'La cantidad conteada no puede ser negativa')
		item.cantidad_conteada = payload.cantidad_conteada
		update_fields.append('cantidad_conteada')

	if update_fields:
		item.save(update_fields=update_fields)

	return item


@router.delete('/items/eliminar/{item_id}', auth=AuthBearer())
def eliminar_item(request, item_id: int):
	item = get_object_or_404(
		ItemConteoStock,
		id=item_id,
		conteo_stock__local__cuenta_id=request.auth.cuenta_id,
	)
	_verificar_acceso_local(request.auth, item.conteo_stock.local_id)

	if item.conteo_stock.estado == ConteoStock.ESTADO_FINALIZADO:
		raise HttpError(400, 'No se puede modificar un conteo finalizado')

	item.delete()
	return {'mensaje': 'Item eliminado'}


# ---------------- Lista de compras ----------------

def _calcular_compras_local(local_id: int, fecha: date_type):
	"""Devuelve los items a comprar de un local en una fecha dada.
	Retorna None si no existe un conteo finalizado para esa fecha."""
	conteo = ConteoStock.objects.filter(
		local_id=local_id,
		fecha=fecha,
		estado=ConteoStock.ESTADO_FINALIZADO,
	).first()
	if conteo is None:
		return None

	plantillas = PlantillaStock.objects.filter(local_id=local_id).select_related('producto')
	cantidades_conteadas = dict(
		ItemConteoStock.objects.filter(conteo_stock=conteo).values_list(
			'producto_id', 'cantidad_conteada'
		)
	)

	items = []
	for plantilla in plantillas:
		actual = cantidades_conteadas.get(plantilla.producto_id, Decimal('0'))
		objetivo = plantilla.cantidad_objetivo
		a_comprar = max(Decimal('0'), objetivo - actual)
		if a_comprar > 0:
			items.append(
				ItemListaCompraSchema(
					producto_id=plantilla.producto_id,
					producto_nombre=plantilla.producto.nombre,
					cantidad_objetivo=float(objetivo),
					cantidad_actual=float(actual),
					cantidad_a_comprar=float(a_comprar),
				)
			)
	return items


@router.get('/comprar/local', response=ListaCompraLocalSchema, auth=AuthBearer())
def lista_compras_local(request, local_id: int, fecha: date_type):
	local = get_object_or_404(Local, id=local_id, cuenta_id=request.auth.cuenta_id)
	_verificar_acceso_local(request.auth, local.id)

	items = _calcular_compras_local(local.id, fecha)
	if items is None:
		raise HttpError(
			404,
			'No existe un conteo finalizado para este local en la fecha indicada',
		)

	return ListaCompraLocalSchema(
		local_id=local.id,
		local_nombre=local.nombre,
		fecha=fecha,
		items=items,
	)


@router.get('/comprar/total', response=ListaCompraTotalSchema, auth=AuthBearer())
def lista_compras_total(request, fecha: date_type):
	locales = list(
		Local.objects.filter(
			id__in=_locales_accesibles_ids(request.auth)
		).order_by('nombre')
	)

	totales = defaultdict(lambda: {'nombre': '', 'cantidad': Decimal('0')})
	locales_sin_conteo = []

	for local in locales:
		items = _calcular_compras_local(local.id, fecha)
		if items is None:
			locales_sin_conteo.append(
				LocalSinConteoSchema(local_id=local.id, local_nombre=local.nombre)
			)
			continue
		for item in items:
			totales[item.producto_id]['nombre'] = item.producto_nombre
			totales[item.producto_id]['cantidad'] += Decimal(str(item.cantidad_a_comprar))

	items_resp = [
		ItemListaCompraTotalSchema(
			producto_id=pid,
			producto_nombre=data['nombre'],
			cantidad_a_comprar=float(data['cantidad']),
		)
		for pid, data in totales.items()
		if data['cantidad'] > 0
	]

	return ListaCompraTotalSchema(
		fecha=fecha,
		items=items_resp,
		locales_sin_conteo_finalizado=locales_sin_conteo,
	)


@router.get('/resumen', response=ResumenLocalFechaSchema, auth=AuthBearer())
def resumen_por_fecha(request, fecha: date_type, local_id: int = None):
	if local_id is not None:
		local = get_object_or_404(Local, id=local_id, cuenta_id=request.auth.cuenta_id)
		_verificar_acceso_local(request.auth, local.id)
		locales = [local]
	else:
		locales = list(
			Local.objects.filter(
				id__in=_locales_accesibles_ids(request.auth)
			).order_by('nombre')
		)

	resumenes = []
	sin_conteo = []

	for local in locales:
		conteo = ConteoStock.objects.filter(
			local_id=local.id,
			fecha=fecha,
			estado=ConteoStock.ESTADO_FINALIZADO,
		).first()

		if conteo is None:
			sin_conteo.append(
				LocalSinConteoSchema(local_id=local.id, local_nombre=local.nombre)
			)
			continue

		plantillas = PlantillaStock.objects.filter(
			local_id=local.id
		).select_related('producto')

		cantidades_conteadas = dict(
			ItemConteoStock.objects.filter(conteo_stock=conteo).values_list(
				'producto_id', 'cantidad_conteada'
			)
		)

		items = []
		for plantilla in plantillas:
			actual = cantidades_conteadas.get(plantilla.producto_id, Decimal('0'))
			objetivo = plantilla.cantidad_objetivo
			a_comprar = max(Decimal('0'), objetivo - actual)
			items.append(
				ItemListaCompraSchema(
					producto_id=plantilla.producto_id,
					producto_nombre=plantilla.producto.nombre,
					cantidad_objetivo=float(objetivo),
					cantidad_actual=float(actual),
					cantidad_a_comprar=float(a_comprar),
				)
			)

		resumenes.append(
			ResumenConteoSchema(
				conteo_id=conteo.id,
				local_id=local.id,
				local_nombre=local.nombre,
				fecha=conteo.fecha,
				estado=conteo.estado,
				items=items,
			)
		)

	return ResumenLocalFechaSchema(
		fecha=fecha,
		locales=resumenes,
		locales_sin_conteo_finalizado=sin_conteo,
	)
