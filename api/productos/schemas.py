from pydantic import BaseModel
from typing import Optional


# REQUEST

class ProductoCreateRequest(BaseModel):
    name: str
    description: str
    price: int
    stock: int
    category_id: int


class CategoriaCreateRequest(BaseModel):
    name: str


# RESPONSE

class ProductoResponse(BaseModel):
    id: int
    name: str
    description: str
    price: int
    stock: int
    category_id: int

    class Config:
        orm_mode = True


class CategoriaResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True