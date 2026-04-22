from ninja import NinjaAPI
from dashboard.api import router

api = NinjaAPI(urls_namespace='dashboard')
api.add_router('/', router)
