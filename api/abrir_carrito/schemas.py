from pydantic import BaseModel
from typing import Optional
from datetime import date


# REQUEST

class UsuariosCreateRequest(BaseModel):
    username: str
    email: str
    password: str

class CarritoCreateRequest(BaseModel):
    user_id: int
    time_tamptz: date

class AgregarItemAlCarritoRequest(BaseModel):
    product_id: int
    quantity: int   

class CarritoDetalleCreateRequest(BaseModel):
    quantity: int
    price: float
    cart_id: int
    product_id: int

class AgregarItemAlCarrito(BaseModel):
    cart_id: int
    product_id: int
    quantity: int
    price: float

class ActualizarCantidadCarritoRequest(BaseModel):
    quantity: int


# RESPONSE

class UsuariosResponse(BaseModel):
    id: int
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True

class CarritoResponse(BaseModel):
    id: int
    user_id: int
    time_tamptz: date

    class Config:
        orm_mode = True


class CarritoDetalleResponse(BaseModel):
    id: int
    quantity: int
    price: float
    cart_id: int
    product_id: int

    class Config:
        orm_mode = True
        