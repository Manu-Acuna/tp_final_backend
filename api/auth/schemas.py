from pydantic import BaseModel, EmailStr
from typing import Optional


# Esquema para la creación de un usuario
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


# Esquema para mostrar la información de un usuario (sin la contraseña)
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True


# Esquema para el token JWT
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

