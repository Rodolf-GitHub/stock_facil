"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from auth.api import router as auth_router
from usuario.api import router as usuario_router
from local.api import router as local_router
from local.usuario_local_api import router as usuario_local_router

api = NinjaAPI()
api.add_router('/auth', auth_router)
api.add_router('/usuarios', usuario_router)
api.add_router('/locales', local_router)
api.add_router('/usuario-local', usuario_local_router)

urlpatterns = [
    path('api/', api.urls),
]
