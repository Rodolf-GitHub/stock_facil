from ninja import Router
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

from auth.auth import AuthBearer
from core.utils.search_filter import search_filter
from producto.models import Producto
from producto.schemas import ProductoSchema, ProductoUpdateSchema

router = Router(tags=['Productos'])


@router.get('/listar', response=list[ProductoSchema], auth=AuthBearer())
@paginate
@search_filter(['nombre'])
def listar_productos(request):
	return Producto.objects.filter(cuenta_id=request.auth.cuenta_id).order_by('-id')


@router.put('/actualizar/{producto_id}', response=ProductoSchema, auth=AuthBearer())
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

	if update_fields:
		producto.save(update_fields=update_fields)

	return producto


@router.delete('/eliminar/{producto_id}', auth=AuthBearer())
def eliminar_producto(request, producto_id: int):
	producto = get_object_or_404(
		Producto,
		id=producto_id,
		cuenta_id=request.auth.cuenta_id,
	)
	producto.delete()
	return {'mensaje': 'Producto eliminado'}
