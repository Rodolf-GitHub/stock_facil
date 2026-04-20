from core.models import BaseModel
from django.db import models

# Create your models here.
class Cuenta(BaseModel):
    nombre = models.CharField(max_length=255)

    class Meta:
        db_table = 'cuenta'
