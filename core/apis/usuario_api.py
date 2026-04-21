from ninja import NinjaAPI
from usuario.api import router

api = NinjaAPI(urls_namespace='usuario')
api.add_router('/', router)
