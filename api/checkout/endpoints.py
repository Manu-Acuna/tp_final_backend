from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.core.database import AsyncSessionLocal
from api.auth.endpoints import get_current_user
from api.productos import dal as productos_dal
from api.core import models
from . import dal, schemas

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/checkout", response_model=schemas.PedidoResponse, status_code=status.HTTP_201_CREATED, summary="Finalizar la compra y crear un pedido.")
async def checkout(checkout_data: schemas.CheckoutRequest, db: AsyncSession = Depends(get_db), current_user: models.Usuarios = Depends(get_current_user)):
    try:
        nuevo_pedido = await dal.procesar_checkout(db=db, user_id=current_user.id, address_id=checkout_data.address_id, payment_method_id=checkout_data.payment_method_id)
        return nuevo_pedido
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al procesar el checkout: {e}")

@router.get("/pedidos",  summary="Obtener todos los pedidos del usuario actual.")
async def obtener_mis_pedidos(db: AsyncSession = Depends(get_db), current_user: models.Usuarios = Depends(get_current_user)):
    try:
        print("pedi")
        pedidos = await dal.obtener_pedidos_de_usuario(db=db, user_id=current_user.id)
        
        return pedidos
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los pedidos: {e}")