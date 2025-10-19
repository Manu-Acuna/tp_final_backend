from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload,joinedload
from api.core import models
from api.checkout import schemas
from datetime import datetime, timezone
from typing import List, Optional
from api.productos.dal import obtener_producto_por_id
from api.core.enum import PedidoStatus, PagoStatus
from sqlalchemy import func
from api.core.dal import obtener_direccion_envio_por_id_y_usuario, obtener_metodo_pago_tipo_por_id
from api.abrir_carrito.dal import obtener_carrito_por_usuario_id, obtener_detalle_carrito, vaciar_carrito_completo


async def procesar_checkout(db: AsyncSession, user_id: int, address_id: int, payment_method_id: int) -> models.Pedidos:
    try:
        #Obtener el carrito
        carrito = await obtener_carrito_por_usuario_id(db, user_id)
        if not carrito: 
            raise ValueError("El usuario no tiene un carrito activo.")
        
        detalles_carrito = await obtener_detalle_carrito(db, carrito.id)
        if not detalles_carrito:
            raise ValueError("El carrito esta vacio.")
        

        #Validar stock y calcular total
        total_pedido = 0.0
        productos_a_actualizar = {}

        for item_carrito in detalles_carrito:
            producto = await obtener_producto_por_id(db, item_carrito.product_id)
            if not producto or producto.stock < item_carrito.quantity:
                raise ValueError(f"No hay suficiente stock para el producto: {item_carrito.product_id} ({producto.name if producto else 'Desconocido'})")
            
            total_pedido += item_carrito.quantity * item_carrito.price
            productos_a_actualizar[producto.id] = producto.stock - item_carrito.quantity
        
        #Crear pedido
        nuevo_pedido = models.Pedidos(
            user_id=user_id,
            address_id=address_id,
            total=total_pedido,
            date=datetime.now(timezone.utc),
            status=PedidoStatus.PENDIENTE.value #1 es pendiente
        )
        db.add(nuevo_pedido)
        await db.flush() #Para obtener el ID del pedido antes del commit

        # Transferir items del carrito a PedidoDetalle y actualizar stock
        for item_carrito in detalles_carrito:
            nuevo_detalle_pedido = models.PedidoDetalle(
                order_id=nuevo_pedido.id,
                product_id=item_carrito.product_id,
                quantity=item_carrito.quantity,
                price=item_carrito.price
            )
            db.add(nuevo_detalle_pedido)

            # Actualizar stock
            producto_db = await obtener_producto_por_id(db, item_carrito.product_id)
            if producto_db:
                producto_db.stock = productos_a_actualizar[producto_db.id]
        
        #Crear registro de pago
        nuevo_pago = models.Pagos(
            order_id=nuevo_pedido.id,
            date=datetime.now(timezone.utc),
            amount=total_pedido,
            status=PagoStatus.APROBADO.value, #1 Aprobado
            payment_method_id=payment_method_id
        )
        db.add(nuevo_pago)
        
        # Vaciar el carrito del usuario
        await vaciar_carrito_completo(db, carrito.id)

        await db.commit()
        
        result = await db.execute(select(models.Pedidos).options(selectinload(models.Pedidos.pedido_detalle), selectinload(models.Pedidos.pagos)).where(models.Pedidos.id == nuevo_pedido.id))
        return result.scalars().first()
    except Exception as e:
        await db.rollback()
        raise e
async def obtener_pedidos_de_usuario(db: AsyncSession, user_id: int, es_admin: bool = False) -> List[models.Pedidos]:
    """Obtiene todos los pedidos de un usuario específico con la direccion del pedido."""
    query = select(models.Pedidos).options(
        joinedload(models.Pedidos.direccion),
        joinedload(models.Pedidos.detalles)
    )

    if not es_admin:
        query = query.where(models.Pedidos.user_id == user_id)

    query = query.order_by(models.Pedidos.id.desc())

    result = await db.execute(query)
    pedidos = result.scalars().unique().all()
    return pedidos

async def obtener_datos_ventas_por_fecha(db: AsyncSession):
    """
    Agrega las ventas totales de pedidos por fecha.
    """
    result = await db.execute(
        select(
            func.date(models.Pedidos.date).label("sale_date"),
            func.sum(models.Pedidos.total).label("total_sales")
        )
        # Puedes filtrar por estado si lo necesitas, ej: .where(models.Pedidos.status == 'completado')
        .group_by(func.date(models.Pedidos.date))
        .order_by(func.date(models.Pedidos.date).asc())
    )
    return result.all()
