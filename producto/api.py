from ninja import Router
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

from auth.auth import AuthBearer, require_admin
from core.utils.search_filter import search_filter
from cuenta.models import Cuenta
from producto.models import Producto
from producto.schemas import ProductoSchema, ProductoCreateSchema, ProductoUpdateSchema

router = Router(tags=['Productos'])


@router.post('/crear', response=ProductoSchema, auth=AuthBearer())
@require_admin
def crear_producto(request, payload: ProductoCreateSchema):
	nombre = payload.nombre.strip()
	if not nombre:
		raise HttpError(400, 'El nombre del producto no puede estar vacio')
	if payload.precio < 0:
		raise HttpError(400, 'El precio no puede ser negativo')

	cuenta = Cuenta.objects.get(id=request.auth.cuenta_id)
	if Producto.objects.filter(cuenta_id=request.auth.cuenta_id).count() >= cuenta.cantidad_maxima_de_productos:
		raise HttpError(400, f'Se alcanzo el limite maximo de {cuenta.cantidad_maxima_de_productos} productos')

	unidad = (payload.unidad_medida or 'unidad').strip() or 'unidad'
	producto = Producto.objects.create(
		nombre=nombre,
		precio=payload.precio,
		unidad_medida=unidad,
		cuenta_id=request.auth.cuenta_id,
	)
	return producto


@router.get('/listar', response=list[ProductoSchema], auth=AuthBearer())
@paginate
@search_filter(['nombre'])
def listar_productos(request):
	return Producto.objects.filter(cuenta_id=request.auth.cuenta_id).order_by('nombre')


@router.put('/actualizar/{producto_id}', response=ProductoSchema, auth=AuthBearer())
@require_admin
def actualizar_producto(request, producto_id: int, payload: ProductoUpdateSchema):
	producto = get_object_or_404(
		Producto,
		id=producto_id,
		cuenta_id=request.auth.cuenta_id,
	)

	update_fields = []

	if payload.nombre is not None:
		nombre = payload.nombre.strip()
		if not nombre:
			raise HttpError(400, 'El nombre del producto no puede estar vacio')
		producto.nombre = nombre
		update_fields.append('nombre')

	if payload.precio is not None:
		if payload.precio < 0:
			raise HttpError(400, 'El precio no puede ser negativo')
		producto.precio = payload.precio
		update_fields.append('precio')

	if payload.unidad_medida is not None:
		unidad = payload.unidad_medida.strip()
		if not unidad:
			raise HttpError(400, 'La unidad de medida no puede estar vacia')
		producto.unidad_medida = unidad
		update_fields.append('unidad_medida')

	if update_fields:
		producto.save(update_fields=update_fields)

	return producto


@router.delete('/eliminar/{producto_id}', auth=AuthBearer())
@require_admin
def eliminar_producto(request, producto_id: int):
	producto = get_object_or_404(
		Producto,
		id=producto_id,
		cuenta_id=request.auth.cuenta_id,
	)
	producto.delete()
	return {'mensaje': 'Producto eliminado'}
