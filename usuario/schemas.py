from ninja import Schema, ModelSchema
from typing import Optional

class UsuarioSchema(ModelSchema):
    class Meta:
        model = 'usuario.Usuario'
        exclude = ['hash_password', 'token']

class UsuarioCreateSchema(Schema):
    cuenta_id: int
    email: str
    password: str

class UsuarioUpdateSchema(Schema):
    email: Optional[str] = None
    password: Optional[str] = None


