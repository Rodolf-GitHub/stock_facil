from django.db import models
from core.models import BaseModel


class UnidadMedida(BaseModel):
    nombre = models.CharField(max_length=50)
    cuenta = models.ForeignKey('cuenta.Cuenta', on_delete=models.CASCADE, related_name='unidades_medida')

    class Meta:
        db_table = 'unidad_medida'
        unique_together = ('nombre', 'cuenta')
