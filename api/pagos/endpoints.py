from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from api.core.database import AsyncSessionLocal
from api.core import models
from api.abrir_carrito import dal as carrito_dal
from api.productos import dal as productos_dal
from api.core.enum import PedidoStatus, PagoStatus

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/pagos/webhook", status_code=status.HTTP_200_OK, summary="Webhook para confirmación de pago", tags=["Pagos"])
async def webhook_confirmacion_pago(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Endpoint que simula la recepción de una notificación de una pasarela de pagos.
    Aquí se procesa la orden, se descuenta el stock y se vacía el carrito.
    """
    data = await request.json()
    user_id = data.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Falta el user_id en la notificación.")

    # --- INICIO DE LA LÓGICA QUE ANTES ESTABA EN "finalizar_compra" ---

    # 1. Obtener carrito y sus items
    carrito = await carrito_dal.obtener_o_crear_carrito(db=db, user_id=user_id)
    if not carrito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado para el usuario.")
        
    items_carrito = await carrito_dal.obtener_detalle_carrito(db=db, carrito_id=carrito.id)
    if not items_carrito:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El carrito está vacío.")

    # 2. Validar stock y calcular total
    total_pedido = 0
    for item in items_carrito:
        producto = await productos_dal.obtener_producto_por_id(db=db, product_id=item.product_id)
        if not producto or producto.stock < item.quantity:
            # En un caso real, se manejaría este error de forma más elegante.
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Stock insuficiente para {producto.name if producto else 'un producto'}.")
        total_pedido += item.price * item.quantity

    # 3. Crear el Pedido
    try:
        # Asumimos que la dirección y método de pago se guardaron temporalmente o se obtienen de otra forma.
        # Para esta simulación, tomamos la primera dirección del usuario.
        direccion = await db.get(models.DireccionesEnvio, data.get("address_id"))
        if not direccion:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dirección no encontrada.")

        nuevo_pedido = models.Pedidos(
            user_id=user_id,
            date=datetime.now(timezone.utc),
            total=total_pedido,
            status=PedidoStatus.COMPLETADO.value, # El pedido ya está pagado
            address_id=direccion.id
        )
        db.add(nuevo_pedido)
        await db.flush()

        # 4. Crear detalles del pedido y **actualizar stock**
        for item in items_carrito:
            db.add(models.PedidoDetalle(order_id=nuevo_pedido.id, product_id=item.product_id, quantity=item.quantity, price=item.price))
            producto = await productos_dal.obtener_producto_por_id(db, item.product_id)
            producto.stock -= item.quantity

        # 5. Vaciar el carrito
        await carrito_dal.vaciar_carrito_completo(db, carrito.id)
        
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear el pedido: {str(e)}")

    return {"status": "ok", "message": "Pedido procesado correctamente."}