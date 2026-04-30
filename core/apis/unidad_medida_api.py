from ninja import NinjaAPI
from unidad_medida.api import router

api = NinjaAPI(urls_namespace='unidad_medida')
api.add_router('/', router)
