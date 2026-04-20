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


class UsuarioRestablecerContrasenaSchema(Schema):
    nueva_password: str


class UsuarioCambiarMiContrasenaSchema(Schema):
    password_actual: str
    nueva_password: str




