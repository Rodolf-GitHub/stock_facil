from django.db import models
from core.models import BaseModel

# Create your models here.
class Local(BaseModel):
    nombre = models.CharField(max_length=255)
    cuenta = models.ForeignKey('cuenta.Cuenta', on_delete=models.CASCADE, related_name='locales')

    class Meta:
        db_table = 'local'
