import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from api.core import models
from api.pedidos_pagos import schemas
from api.abrir_carrito import dal as carrito_dal
from api.core.models import Pedidos, Pagos, PedidoDetalle


async def crear_pedido(db: AsyncSession, pedido: schemas.PedidosCreateRequest):
    db_pedido = models.Pedidos(**pedido.dict())
    db.add(db_pedido)
    await db.commit()
    await db.refresh(db_pedido)
    return db_pedido


async def obtener_pedido_por_id(db: AsyncSession, pedido_id: int, user_id: int):
    query = (select(Pedidos).options(selectinload(Pedidos.pedido_detalle).joinedload(PedidoDetalle.producto), selectinload(Pedidos.pago)).where(Pedidos.id == pedido_id, Pedidos.user_id == user_id))
    result = await db.execute(query)
    return result.scalars().first()


async def crear_pedido_desde_carrito(db: AsyncSession, user_id: int, address_id: int):
    carrito = await carrito_dal.obtener_carrito_por_usuario_id(db, user_id=user_id)
    
    if not carrito:
        raise HTTPException(status_code=404, detail="No se encontró el carrito para el usuario.")

    query = (select(models.CarritoDetalle).options(joinedload(models.CarritoDetalle.producto)).where(models.CarritoDetalle.cart_id == carrito.id))
    result = await db.execute(query)
    items_carrito = result.scalars().all()
    if not items_carrito:
        raise HTTPException(status_code=404, detail="No se encontraron productos en el carrito.")

    total_pedido = 0
    for item in items_carrito:
        if item.producto.stock < item.quantity:
            raise HTTPException(status_code=409, detail=f"No hay suficiente stock para el producto {item.producto.name}.")
        total_pedido += item.quantity * item.producto.price
    
    nuevo_pedido = models.Pedidos(date = datetime.datetime.now(), total = total_pedido, status = 1, user_id = user_id, address_id = address_id)
    db.add(nuevo_pedido)
    await db.flush()

    for item in items_carrito:
        detalle_pedido = PedidoDetalle(quantity = item.quantity, price = item.producto.price, order_id = nuevo_pedido.id, product_id = item.product_id)
        db.add(detalle_pedido)
        
        item.producto.stock -= item.quantity
       
        await db.delete(item)

    await db.commit()

    query_final = (select(models.Pedidos).options(selectinload(models.Pedidos.pedido_detalle).joinedload(models.PedidoDetalle.producto)).where(models.Pedidos.id == nuevo_pedido.id))
    resultado_final = await db.execute(query_final)
    return resultado_final.scalars().first()


async def registrar_pago_para_pedido(db: AsyncSession, pedido: Pedidos, payment_method_id: int):
    if pedido.status != 1:
        raise HTTPException(status_code=409, detail="Este pedido esta siendo procesado")
    
    nuevo_pago = Pagos(date = datetime.datetime.now(), amount = pedido.total, status = 1, order_id = pedido.id, payment_method_id = payment_method_id)
    db.add(nuevo_pago)

    pedido.status = 2

    await db.commit()

    await db.refresh(pedido, attribute_names=["pago", "status"])

    return pedido



