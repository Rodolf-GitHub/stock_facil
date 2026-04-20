from ninja import Schema, ModelSchema
from typing import Optional
from local.models import Local


class LocalSchema(ModelSchema):
	class Meta:
		model = Local
		fields = "__all__"


class LocalCreateSchema(Schema):
	nombre: str


class LocalUpdateSchema(Schema):
	nombre: Optional[str] = None
