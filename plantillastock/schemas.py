from ninja import Schema, ModelSchema
from typing import Optional
from datetime import datetime
from plantillastock.models import PlantillaStock


class PlantillaStockSchema(Schema):
	id: int
	local_id: int
	producto_id: int
	producto_nombre: str
	producto_unidad_medida: str
	cantidad_objetivo: float
	created_at: datetime
	updated_at: datetime

	@staticmethod
	def resolve_producto_nombre(obj):
		return obj.producto.nombre

	@staticmethod
	def resolve_producto_unidad_medida(obj):
		return obj.producto.unidad_medida


class PlantillaStockCreateSchema(Schema):
	local_id: int
	producto_id: int
	cantidad_objetivo: float


class PlantillaStockUpdateSchema(Schema):
	cantidad_objetivo: Optional[float] = None
