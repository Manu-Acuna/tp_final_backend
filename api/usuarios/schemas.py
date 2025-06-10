from  pydantic import BaseModel
from typing import Optional


# REQUEST

class UsuariosCreateRequest(BaseModel):
    username: str
    email: str
    password: str
    registry_date: Optional[str] = None
    rol_id: int


class RolesCreateRequest(BaseModel):
    name: str

# RESPONSE

class UsuariosResponse(BaseModel):
    id: int
    username: str
    email: str
    password: str
    registry_date: Optional[str]
    rol_id: int
    
    class Config:
        orm_mode = True


class RolesResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True



