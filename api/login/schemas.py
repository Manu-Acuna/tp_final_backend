from pydantic import BaseModel
from typing import Optional
from datetime import date


# REQUEST

class UsuariosCreateRequest(BaseModel):
    username: str
    email: str
    password: str


class DireccionesEnvioCreateRequest(BaseModel):
    address: str
    city: str
    zip_code: str
    user_id: int


# RESPONSE

class UsuariosResponse(BaseModel):
    id: int
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True


class DireccionesEnvioResponse(BaseModel):
    id: int
    address: str
    city: str
    zip_code: str
    usuario_id: int

    class Config:
        orm_mode = True
