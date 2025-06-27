from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from api.core import models
from api.abrir_carrito import schemas


async def obtener_o_crear_carrito(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.Carrito).where(models.Carrito.user_id == user_id))
    carrito = result.scalars().first()
    if carrito is not None:
        return carrito
    
    db_carrito = models.Carrito(user_id=user_id, time_tamptz=datetime.now(timezone.utc))
    db.add(db_carrito)
    await db.commit()
    await db.refresh(db_carrito)
    
    return db_carrito


async def calcular_total_carrito(db: AsyncSession, carrito_id: int) -> float:
    detalles = await obtener_detalle_carrito(db=db, carrito_id=carrito_id)
    total = 0.0
    for item in detalles:
        total += item.quantity * item.price
    return total


async def obtener_carrito_por_usuario_id(db: AsyncSession, user_id: int): #user_id va a venir desde el endpoint
    query = select(models.Carrito).options(selectinload(models.Carrito.usuario)).where(models.Carrito.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().first()


async def agregar_item_al_carrito(db: AsyncSession, cart_id: int, product_id: int, quantity: int, price: float):
    result = await db.execute(select(models.CarritoDetalle).where(models.CarritoDetalle.cart_id == cart_id, models.CarritoDetalle.product_id == product_id))
    item_existente = result.scalars().first()
    if item_existente:
        item_existente.quantity += quantity
        db_item = item_existente
    else:
        db_item = models.CarritoDetalle(cart_id=cart_id, product_id=product_id, quantity=quantity, price=price)
        db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def obtener_detalle_carrito(db: AsyncSession, carrito_id: int): # carrito_id va a venir desde el endpoint
    query = select(models.CarritoDetalle).options(selectinload(models.CarritoDetalle.carrito)).where(models.CarritoDetalle.cart_id == carrito_id)
    result = await db.execute(query)
    return result.scalars().all()


async def obtener_detalle_carrito_por_id(db: AsyncSession, carrito_detalle_id: int):
    """Obtiene un detalle de carrito específico por su ID."""
    query = select(models.CarritoDetalle).where(models.CarritoDetalle.id == carrito_detalle_id)
    result = await db.execute(query)
    return result.scalars().first()


async def eliminar_item_del_carrito(db: AsyncSession, carrito_detalle: models.CarritoDetalle):
    """Elimina un objeto CarritoDetalle de la base de datos."""
    await db.delete(carrito_detalle)
    await db.commit()
    return True 


async def actualizar_cantidad_item_carrito(db: AsyncSession, carrito_detalle: models.CarritoDetalle, nueva_cantidad: int, precio_unitario_producto: float):
    """Actualiza la cantidad y el precio total de un item en el carrito."""
    carrito_detalle.quantity = nueva_cantidad
    await db.commit()
    await db.refresh(carrito_detalle)
    
    result = await db.execute(select(models.CarritoDetalle).options(selectinload(models.CarritoDetalle.carrito), selectinload(models.CarritoDetalle.producto)).where(models.CarritoDetalle.id == carrito_detalle.id))
    return result.scalars().first()


async def vaciar_carrito_completo(db: AsyncSession, carrito_id: int):
    """Elimina todos los CarritoDetalle asociados a un carrito_id."""
    
    items_a_eliminar = await db.execute(select(models.CarritoDetalle).where(models.CarritoDetalle.cart_id == carrito_id))
    for item in items_a_eliminar.scalars().all():
        await db.delete(item)
    await db.commit()
    return True