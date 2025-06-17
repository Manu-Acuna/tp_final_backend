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


