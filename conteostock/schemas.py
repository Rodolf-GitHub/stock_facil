from ninja import Schema, ModelSchema
from typing import Optional
from datetime import date
from conteostock.models import ConteoStock, ItemConteoStock


class ConteoStockSchema(ModelSchema):
	class Meta:
		model = ConteoStock
		fields = '__all__'


class ItemConteoStockSchema(ModelSchema):
	class Meta:
		model = ItemConteoStock
		fields = '__all__'


class ConteoStockCreateSchema(Schema):
	local_id: int
	fecha: Optional[date] = None


class ConteoStockUpdateSchema(Schema):
	fecha: Optional[date] = None


class ItemConteoStockCreateSchema(Schema):
	conteo_stock_id: int
	producto_id: int
	cantidad_conteada: float


class ItemConteoStockUpdateSchema(Schema):
	cantidad_conteada: Optional[float] = None


class ItemListaCompraSchema(Schema):
	producto_id: int
	producto_nombre: str
	cantidad_objetivo: float
	cantidad_actual: float
	cantidad_a_comprar: float


class ListaCompraLocalSchema(Schema):
	local_id: int
	local_nombre: str
	fecha: date
	items: list[ItemListaCompraSchema]


class ItemListaCompraTotalSchema(Schema):
	producto_id: int
	producto_nombre: str
	cantidad_a_comprar: float


class ResumenConteoSchema(Schema):
	conteo_id: int
	local_id: int
	local_nombre: str
	fecha: date
	estado: str
	items: list[ItemListaCompraSchema]
