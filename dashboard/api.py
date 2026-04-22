from decimal import Decimal

from ninja import Router
from django.utils import timezone

from auth.auth import AuthBearer
from cuenta.models import Cuenta
from local.models import Local, UsuarioLocal
from producto.models import Producto
from plantillastock.models import PlantillaStock
from conteostock.models import ConteoStock, ItemConteoStock
from dashboard.schemas import DashboardSchema, LocalEstadisticasSchema

router = Router(tags=['Dashboard'])


def _locales_accesibles(usuario):
	if usuario.es_admin:
		return Local.objects.filter(cuenta_id=usuario.cuenta_id)
	local_ids = UsuarioLocal.objects.filter(
		usuario_id=usuario.id,
		local__cuenta_id=usuario.cuenta_id,
	).values_list('local_id', flat=True)
	return Local.objects.filter(id__in=local_ids)


def _calcular_a_comprar(local_id, fecha):
	plantillas = PlantillaStock.objects.filter(local_id=local_id)
	conteo = ConteoStock.objects.filter(local_id=local_id, fecha=fecha).first()
	cantidades = {}
	if conteo:
		cantidades = dict(
			ItemConteoStock.objects.filter(conteo_stock=conteo).values_list(
				'producto_id', 'cantidad_conteada'
			)
		)
	pendientes = 0
	for p in plantillas:
		actual = cantidades.get(p.producto_id, Decimal('0'))
		if p.cantidad_objetivo - actual > 0:
			pendientes += 1
	return pendientes


@router.get('/estadisticas', response=DashboardSchema, auth=AuthBearer())
def obtener_estadisticas(request):
	usuario = request.auth
	cuenta = Cuenta.objects.get(id=usuario.cuenta_id)
	hoy = timezone.now().date()

	locales = list(_locales_accesibles(usuario).order_by('nombre'))
	locales_ids = [l.id for l in locales]

	total_productos = Producto.objects.filter(cuenta_id=usuario.cuenta_id).count()

	conteos_qs = ConteoStock.objects.filter(local_id__in=locales_ids)
	total_borrador = conteos_qs.filter(estado=ConteoStock.ESTADO_BORRADOR).count()
	total_finalizados = conteos_qs.filter(estado=ConteoStock.ESTADO_FINALIZADO).count()

	locales_stats = []
	total_a_comprar_hoy = 0
	for local in locales:
		ultimo = (
			ConteoStock.objects.filter(local_id=local.id)
			.order_by('-fecha', '-id')
			.first()
		)
		productos_plantilla = PlantillaStock.objects.filter(local_id=local.id).count()
		total_conteos = ConteoStock.objects.filter(local_id=local.id).count()
		a_comprar = _calcular_a_comprar(local.id, hoy)
		total_a_comprar_hoy += a_comprar

		locales_stats.append(
			LocalEstadisticasSchema(
				local_id=local.id,
				local_nombre=local.nombre,
				productos_en_plantilla=productos_plantilla,
				ultimo_conteo_fecha=ultimo.fecha if ultimo else None,
				ultimo_conteo_estado=ultimo.estado if ultimo else None,
				total_conteos=total_conteos,
				productos_a_comprar_hoy=a_comprar,
			)
		)

	return DashboardSchema(
		cuenta_nombre=cuenta.nombre,
		total_productos=total_productos,
		total_locales_accesibles=len(locales),
		total_conteos_borrador=total_borrador,
		total_conteos_finalizados=total_finalizados,
		productos_a_comprar_hoy=total_a_comprar_hoy,
		locales=locales_stats,
	)
