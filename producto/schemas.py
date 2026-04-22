from ninja import Schema, ModelSchema
from typing import Optional
from producto.models import Producto


class ProductoSchema(ModelSchema):
	class Meta:
		model = Producto
		fields = '__all__'


class ProductoCreateSchema(Schema):
	nombre: str
	precio: float
	unidad_medida: Optional[str] = 'unidad'


class ProductoUpdateSchema(Schema):
	nombre: Optional[str] = None
	precio: Optional[float] = None
	unidad_medida: Optional[str] = None
