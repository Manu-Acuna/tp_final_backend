from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from api.core import models
from api.abrir_carrito import schemas


async def crear_carrito(db: AsyncSession, carrito: schemas.CarritoCreateRequest):
    db_carrito = models.Carrito(**carrito.dict())
    db.add(db_carrito)
    await db.commit()
    await db.refresh(db_carrito)
    
    result = await db.execute(select(models.Carrito).options(selectinload(models.Carrito.usuario)).where(models.Carrito.id == db_carrito.id))
    return result.scalars().first()


async def obtener_carrito_por_usuario_id(db: AsyncSession, user_id: int): #user_id va a venir desde el endpoint
    query = select(models.Carrito).options(selectinload(models.Carrito.usuario)).where(models.Carrito.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().first()


async def crear_carrito_detalle(db: AsyncSession, carrito_detalle: schemas.CarritoDetalleCreateRequest):
    db_carrito_detalle = models.CarritoDetalle(**carrito_detalle.dict())
    db.add(db_carrito_detalle)
    await db.commit()
    await db.refresh(db_carrito_detalle)
    
    result = await db.execute(select(models.CarritoDetalle).options(selectinload(models.CarritoDetalle.carrito)).where(models.CarritoDetalle.id == db_carrito_detalle.id))
    return result.scalars().first()


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
    carrito_detalle.price = nueva_cantidad * precio_unitario_producto
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