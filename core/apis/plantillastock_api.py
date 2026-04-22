from ninja import NinjaAPI
from plantillastock.api import router

api = NinjaAPI(urls_namespace='plantillastock')
api.add_router('/', router)
