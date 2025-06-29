from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.core import models
from . import schemas

async def crear_metodo_pago(db: AsyncSession, metodo_pago: schemas.MetodoPagoCreateRequest):
    nuevo_metodo_pago = models.MetodosPago(**metodo_pago.dict())
    db.add(nuevo_metodo_pago)
    await db.commit()
    await db.refresh(nuevo_metodo_pago)
    return nuevo_metodo_pago

async def obtener_metodos_pago(db: AsyncSession):
    result = await db.execute(select(models.MetodosPago))
    return result.scalars().all()

async def actualizar_metodo_pago(db: AsyncSession, metodo_pago_id: int, metodo_pago_data: schemas.MetodoPagoCreateRequest):
    """Actualiza un método de pago existente."""
    db_metodo_pago = await db.get(models.MetodosPago, metodo_pago_id)
    if db_metodo_pago:
        db_metodo_pago.name = metodo_pago_data.name
        await db.commit()
        await db.refresh(db_metodo_pago)
    return db_metodo_pago