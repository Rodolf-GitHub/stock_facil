from ninja import NinjaAPI
from conteostock.api import router

api = NinjaAPI(urls_namespace='conteostock')
api.add_router('/', router)
