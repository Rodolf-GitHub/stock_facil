from ninja import NinjaAPI
from local.api import router
from local.usuario_local_api import router as usuario_local_router

api = NinjaAPI(urls_namespace='local')
api.add_router('/', router)
api.add_router('/usuario-local', usuario_local_router)
