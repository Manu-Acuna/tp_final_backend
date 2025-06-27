from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# REQUEST

class AgregarItemAlCarritoRequest(BaseModel):
    product_id: int
    quantity: int   

class FinalizarCompraRequest(BaseModel):
    address_id: int
    payment_method_id: int

class ActualizarCantidadCarritoRequest(BaseModel):
    quantity: int


# RESPONSE



class CarritoResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class CarritoTotalResponse(BaseModel):
    cart_id: int
    total_price: float

    class Config:
        orm_mode = True

class CarritoDetalleResponse(BaseModel):
    id: int
    quantity: int
    price: float
    cart_id: int
    product_id: int
    product_name: str
    image_url: Optional[str] = None

    class Config:
        orm_mode = True

class FinalizarCompraResponse(BaseModel):
    message: str
    order_id: int
        