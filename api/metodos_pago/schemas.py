from pydantic import BaseModel

# REQUEST
class MetodoPagoCreateRequest(BaseModel):
    name: str

# RESPONSE
class MetodoPagoResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True