from ninja import Schema, ModelSchema
from typing import Optional
from plantillastock.models import PlantillaStock


class PlantillaStockSchema(ModelSchema):
	class Meta:
		model = PlantillaStock
		fields = '__all__'


class PlantillaStockCreateSchema(Schema):
	local_id: int
	producto_id: int
	cantidad_objetivo: float


class PlantillaStockUpdateSchema(Schema):
	cantidad_objetivo: Optional[float] = None
