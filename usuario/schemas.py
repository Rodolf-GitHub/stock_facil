from ninja import Schema, ModelSchema
from typing import Optional
from usuario.models import Usuario

class UsuarioSchema(ModelSchema):
    class Meta:
        model = Usuario
        exclude = ['hash_password', 'token']

class UsuarioCreateSchema(Schema):
    email: str
    password: str

class UsuarioUpdateSchema(Schema):
    email: Optional[str] = None
    password: Optional[str] = None


