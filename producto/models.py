from django.db import models
from core.models import BaseModel
# Create your models here.
class Producto(BaseModel):
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=50, default='unidades')
    cuenta = models.ForeignKey('cuenta.Cuenta', on_delete=models.CASCADE, related_name='productos')

    class Meta:
        db_table = 'producto'
