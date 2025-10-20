from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# REQUEST
class DireccionEnvioCreateRequest(BaseModel):
    address: str
    city: str
    zip_code: str

class UserUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None

# RESPONSE
class DireccionEnvioResponse(BaseModel):
    id: int
    address: str
    city: str
    zip_code: str

    class Config:
        from_attributes = True

class User(BaseModel):
    id: int
    email: EmailStr
    nombre: str
    apellido: str
    is_admin: bool
    fecha_nacimiento: datetime

    class Config:
        from_attributes = True