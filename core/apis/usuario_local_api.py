from ninja import NinjaAPI
from local.usuario_local_api import router

api = NinjaAPI(urls_namespace='usuario_local')
api.add_router('/', router)
