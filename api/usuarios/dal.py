from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.core import models
from . import schemas

async def crear_direccion_envio(db: AsyncSession, direccion: schemas.DireccionEnvioCreateRequest, user_id: int):
    nueva_direccion = models.DireccionesEnvio(
        **direccion.dict(),
        user_id=user_id
    )
    db.add(nueva_direccion)
    await db.commit()
    await db.refresh(nueva_direccion)
    return nueva_direccion

async def obtener_direcciones_por_usuario(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.DireccionesEnvio).where(models.DireccionesEnvio.user_id == user_id))
    return result.scalars().all()