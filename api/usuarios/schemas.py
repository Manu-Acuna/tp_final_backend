from pydantic import BaseModel

# REQUEST
class DireccionEnvioCreateRequest(BaseModel):
    address: str
    city: str
    zip_code: str

# RESPONSE
class DireccionEnvioResponse(BaseModel):
    id: int
    address: str
    city: str
    zip_code: str

    class Config:
        orm_mode = True