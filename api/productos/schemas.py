from pydantic import BaseModel
from typing import Optional


# REQUEST

class ProductoCreateRequest(BaseModel):
    name: str
    description: str
    price: int
    stock: int
    image_url: Optional[str] = None
    category_id: int


class ProductoUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None


class CategoriaCreateRequest(BaseModel):
    name: str


# RESPONSE

class ProductoResponse(BaseModel):
    id: int
    name: str
    description: str
    price: int
    stock: int
    image_url: Optional[str] = None
    category_id: int

    class Config:
        orm_mode = True


class CategoriaResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True