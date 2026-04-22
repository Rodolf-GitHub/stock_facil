from ninja import Schema
from datetime import date
from typing import Optional


class LocalEstadisticasSchema(Schema):
	local_id: int
	local_nombre: str
	productos_en_plantilla: int
	ultimo_conteo_fecha: Optional[date] = None
	ultimo_conteo_estado: Optional[str] = None
	total_conteos: int
	productos_a_comprar_hoy: int


class DashboardSchema(Schema):
	cuenta_nombre: str
	total_productos: int
	total_locales_accesibles: int
	total_conteos_borrador: int
	total_conteos_finalizados: int
	productos_a_comprar_hoy: int
	locales: list[LocalEstadisticasSchema]
