from django.db import models
from core.models import BaseModel

# Create your models here.
class Local(BaseModel):
    nombre = models.CharField(max_length=255)
    cuenta = models.ForeignKey('cuenta.Cuenta', on_delete=models.CASCADE, related_name='locales')

    class Meta:
        db_table = 'local'

class UsuarioLocal(BaseModel):
    usuario = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE, related_name='locales_asignados')
    local = models.ForeignKey('local.Local', on_delete=models.CASCADE, related_name='usuarios_asignados')
