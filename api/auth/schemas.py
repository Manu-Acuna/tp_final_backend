from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class UserBase(BaseModel):
    email: EmailStr
    nombre: str
    apellido: str


class UserCreate(UserBase):
    password: str
    fecha_nacimiento: date


class UserResponse(UserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
