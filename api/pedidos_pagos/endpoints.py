from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.core.database import AsyncSessionLocal
from api.core import models
from api.abrir_carrito.endpoints import obtener_usuario_activo
from . import dal, schemas

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos y Pagos"],
    responses={404: {"description": "No encontrado"}},
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.PedidoCompletoResponse, status_code=201)
async def generar_pedido_desde_carrito(
    pedido_data: schemas.PedidoDesdeCarritoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuarios = Depends(obtener_usuario_activo)
):
   
    try:
        pedido_creado = await dal.crear_pedido_desde_carrito(
            db=db,
            user_id=current_user.id,
            address_id=pedido_data.address_id
        )

        detalles_respuesta = [
            schemas.PedidoDetalleCompletoResponse(
                id=detalle.id,
                quantity=detalle.quantity,
                price=detalle.price,
                product_id=detalle.product_id,
                product_name=detalle.producto.name
            ) for detalle in pedido_creado.pedido_detalle
        ]

        return schemas.PedidoCompletoResponse.from_orm(pedido_creado)

    except HTTPException as e:
        
        raise e
    except Exception as e:
        
        raise HTTPException(status_code=500, detail="Ocurrió un error interno al procesar el pedido.")


@router.post("/{id_del_pedido}/pagar", response_model=schemas.PedidoCompletoResponse)
async def procesar_pago_pedido(id_del_pedido: int, pago_data:schemas.ProcesarPagoRequest, db: AsyncSession = Depends(get_db), current_user: models.Usuarios = Depends(obtener_usuario_activo)):
    pedido = await dal.obtener_pedido_por_id(db, pedido_id=id_del_pedido, user_id=current_user.id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    try:
        pedido_pagado = await dal.registrar_pago_para_pedido(db, pedido = pedido, payment_method_id=pago_data.payment_method_id)
        return schemas.PedidoCompletoResponse.from_orm(pedido_pagado)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ocurrió un error al procesar el pago")