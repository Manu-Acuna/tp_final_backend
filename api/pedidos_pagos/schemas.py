from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime


#Metodo de pago

class MetodoPagoCreateRequest(BaseModel):
    name: str

class MetodoPagoResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

#Pedido detalle

class PedidoDetalleCreateRequest(BaseModel):
    quantity: int
    price: float
    order_id: int
    product_id: int

class PedidoDetalleResponse(BaseModel):
    id: int
    quantity: int
    price: float
    # order_id: int
    product_id: int

    class Config:
        orm_mode = True        

class PedidoDetalleCompletoResponse(BaseModel):
    id: int
    quantity: int
    price: float
    order_id: int
    product_id: int

#Pedidos

class PedidosCreateRequest(BaseModel):
    date: datetime
    total: float
    status: int
    user_id: int
    address_id: int


class PedidosResponse(BaseModel):
    id: int
    date: datetime
    total: float
    status: int
    user_id: int
    address_id: int
    pedido_detalle: List[PedidoDetalleResponse] = []

    class Config:
        orm_mode = True

class PedidoDesdeCarritoCreate(BaseModel):
    address_id: int

class PedidoCompletoResponse(PedidosResponse):
    pedido_detalle: List[PedidoDetalleCompletoResponse] = []
    pago: Optional['PagosResponse'] = None

class ProcesarPagoRequest(BaseModel):
    payment_method_id: int



#Pagos

class PagosCreateRequest(BaseModel):
    date:datetime
    amount: float
    status: int
    order_id: int
    payment_method_id: int


class PagosResponse(BaseModel):
    id: int
    date: datetime
    amount: float
    status: int
    order_id: int
    payment_method_id: int

    class Config:
        orm_mode = True


PedidoCompletoResponse.update_forward_refs()