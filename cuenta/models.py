from core.models import BaseModel
from django.db import models

# Create your models here.
class Cuenta(BaseModel):
    nombre = models.CharField(max_length=255, unique=True)
    cantidad_maxima_de_productos = models.IntegerField(default=300)
    cantidad_maxima_de_locales = models.IntegerField(default=5)
    cantidad_maxima_de_usuarios = models.IntegerField(default=10)
    cantidad_maxima_de_conteo_stock = models.IntegerField(default=1000)

    class Meta:
        db_table = 'cuenta'
