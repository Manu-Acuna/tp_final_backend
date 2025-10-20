from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from api.core.database import get_db
from api.auth.endpoints import get_current_user, get_current_admin_user
from api.productos import dal as productos_dal
from api.core import models
from . import dal, schemas

router = APIRouter()

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
        pedidos = await dal.obtener_pedidos_de_usuario(db=db, user_id=current_user.id, es_admin=current_user.is_admin)
        
        return pedidos
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los pedidos: {e}")


@router.get("/pedidos/{order_id}", response_model=schemas.PedidoDetalladoResponse, summary="Obtener detalles de un pedido específico", tags=["Pedidos"])
async def obtener_detalle_pedido(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuarios = Depends(get_current_user)
):
    """
    Obtiene la información completa de un pedido, incluyendo los productos comprados.
    Solo el usuario que realizó el pedido o un administrador pueden verlo.
    """
    query = (
        select(models.Pedidos)
        .where(models.Pedidos.id == order_id)
        .options(
            selectinload(models.Pedidos.detalles)
            .selectinload(models.PedidoDetalle.producto)
        ,
            selectinload(models.Pedidos.pagos))
    )
    result = await db.execute(query)
    pedido = result.scalars().first()

    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado.")
    if pedido.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para ver este pedido.")
        
    return pedido

@router.get("/pedidos/admin/datos-ventas/", response_model=list[schemas.DatosVentas], summary="Obtener datos de ventas agregados por día (Admin)", tags=["Admin"])
async def obtener_datos_ventas(
    db: AsyncSession = Depends(get_db),
    current_admin: models.Usuarios = Depends(get_current_admin_user)
):
    """
    Devuelve una lista de objetos con la fecha y el total de ventas para esa fecha.
    Solo los administradores pueden acceder a este endpoint.
    """
    datos_ventas = await dal.obtener_datos_ventas_por_fecha(db)
    return [schemas.DatosVentas(date=row.sale_date, total_sales=row.total_sales) for row in datos_ventas]
