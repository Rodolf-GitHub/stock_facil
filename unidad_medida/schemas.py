from ninja import Schema, ModelSchema
from typing import Optional
from datetime import datetime
from unidad_medida.models import UnidadMedida


class UnidadMedidaSchema(ModelSchema):
	class Meta:
		model = UnidadMedida
		fields = ['id', 'nombre', 'created_at', 'updated_at']


class UnidadMedidaCreateSchema(Schema):
	nombre: str


class UnidadMedidaUpdateSchema(Schema):
	nombre: Optional[str] = None
