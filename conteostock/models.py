from django.db import models
from core.models import BaseModel
from django.utils import timezone
# Create your models here.
class ConteoStock(BaseModel):
    ESTADO_BORRADOR = 'borrador'
    ESTADO_FINALIZADO = 'finalizado'
    ESTADO_CHOICES = [
        (ESTADO_BORRADOR, 'Borrador'),
        (ESTADO_FINALIZADO, 'Finalizado'),
    ]

    local = models.ForeignKey('local.Local', on_delete=models.CASCADE, related_name='conteos_stock')
    fecha = models.DateField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_BORRADOR)
    creado_por = models.ForeignKey('usuario.Usuario', on_delete=models.SET_NULL, null=True, related_name='conteos_stock_creados')

    class Meta:
        db_table = 'conteo_stock'
        unique_together = ('local', 'fecha')

class ItemConteoStock(BaseModel):
    conteo_stock = models.ForeignKey(ConteoStock, on_delete=models.CASCADE, related_name='items_conteo_stock')
    producto = models.ForeignKey('producto.Producto', on_delete=models.CASCADE, related_name='items_conteo_stock')
    cantidad_conteada = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'item_conteo_stock'
        unique_together = ('conteo_stock', 'producto')
