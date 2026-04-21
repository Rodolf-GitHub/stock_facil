from ninja import NinjaAPI
from producto.api import router

api = NinjaAPI(urls_namespace='producto')
api.add_router('/', router)
