from pydantic import BaseModel
from typing import List,Optional
from datetime import datetime, date
class CheckoutRequest(BaseModel):
    address_id: int
    payment_method_id: int

# RESPONSE

class PagoResponse(BaseModel):
    id: int
    date: datetime
    amount: float
    status: int
    payment_method_id: int

    class Config:
        from_attributes = True


class PedidoDetalleResponse(BaseModel):
    id: int
    quantity: int
    price: float
    order_id: int
    product_id: int

    class Config:
        from_attributes = True


class PedidoResponse(BaseModel):
    id: int
    date: datetime
    total:float
    status: int
    user_id: int
    address_id: int
    detalles:list[PedidoDetalleResponse] = []
    pagos: list[PagoResponse] = []


    class Config:
        from_attributes = True
class ListaPedidosResponse(BaseModel):
    pedidos: List[PedidoResponse]        