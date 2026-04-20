from ninja import Schema
from typing import Optional

class LoginSchema(Schema):
    email: str
    password: str

class LoginResponseSchema(Schema):
    token: str
    usuario_id: int
    email: str
    es_admin: bool
