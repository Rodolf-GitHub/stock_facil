from django.db import models
from core.models import BaseModel
# Create your models here.
class PlantillaStock(BaseModel):
    local= models.ForeignKey('local.Local', on_delete=models.CASCADE, related_name='plantillas_stock')
    producto = models.ForeignKey('producto.Producto', on_delete=models.CASCADE, related_name='plantillas_stock')
    cantidad_objetivo = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'plantilla_stock'
