from ninja import NinjaAPI
from auth.api import router

api = NinjaAPI(urls_namespace='auth')
api.add_router('/', router)
