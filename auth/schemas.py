from ninja import Schema, ModelSchema
from typing import Optional
from models import Usuario
from usuario.schemas import UsuarioSchema

class LoginSchema(Schema):
    email: str
    password: str

class LoginResponseSchema(Schema):
    token: str
    usuario: UsuarioSchema 
