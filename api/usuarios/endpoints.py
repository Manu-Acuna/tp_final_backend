from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from api.core.database import AsyncSessionLocal
from api.auth.endpoints import get_current_user
from api.core import models
from . import dal, schemas

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/me/direcciones", response_model=schemas.DireccionEnvioResponse, status_code=status.HTTP_201_CREATED, summary="Crear una nueva dirección de envío para el usuario actual")
async def crear_direccion_para_usuario_actual(
    direccion: schemas.DireccionEnvioCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuarios = Depends(get_current_user)
):
    return await dal.crear_direccion_envio(db=db, direccion=direccion, user_id=current_user.id)

@router.get("/me/direcciones", response_model=List[schemas.DireccionEnvioResponse], summary="Listar las direcciones de envío del usuario actual")
async def listar_direcciones_del_usuario_actual(
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuarios = Depends(get_current_user)
):
    return await dal.obtener_direcciones_por_usuario(db=db, user_id=current_user.id)