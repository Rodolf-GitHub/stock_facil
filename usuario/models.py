from django.db import models
from core.models import BaseModel
# Create your models here.
class Usuario(BaseModel):
    cuenta = models.ForeignKey('cuenta.Cuenta', on_delete=models.CASCADE, related_name='usuarios')
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'usuario'
