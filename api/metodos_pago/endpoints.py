from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from api.core.database import AsyncSessionLocal
from . import dal, schemas

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/metodos_pago/", response_model=schemas.MetodoPagoResponse, status_code=status.HTTP_201_CREATED, tags=["Metodos de Pago"])
async def crear_metodo_pago(metodo_pago: schemas.MetodoPagoCreateRequest, db: AsyncSession = Depends(get_db)):
    # En una aplicación real, aquí se debería verificar si el usuario es administrador.
    db_metodo_pago = await dal.crear_metodo_pago(db=db, metodo_pago=metodo_pago)
    return db_metodo_pago

@router.get("/metodos_pago/", response_model=List[schemas.MetodoPagoResponse], tags=["Metodos de Pago"])
async def listar_metodos_pago(db: AsyncSession = Depends(get_db)):
    metodos_pago = await dal.obtener_metodos_pago(db=db)
    return metodos_pago

@router.put("/metodos_pago/{metodo_pago_id}", response_model=schemas.MetodoPagoResponse, tags=["Metodos de Pago"], summary="Actualizar un método de pago")
async def actualizar_metodo_pago(
    metodo_pago_id: int,
    metodo_pago_data: schemas.MetodoPagoCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    db_metodo_pago = await dal.actualizar_metodo_pago(db=db, metodo_pago_id=metodo_pago_id, metodo_pago_data=metodo_pago_data)
    if db_metodo_pago is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Método de pago no encontrado")
    return db_metodo_pago
