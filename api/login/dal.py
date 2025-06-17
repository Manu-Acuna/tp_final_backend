from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from api.core import models
from api.login import schemas


async def crear_usuario(db: AsyncSession, usuario: schemas.UsuariosCreateRequest):
    nuevo_usuario = models.Usuarios(**usuario.dict())
    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)

    return nuevo_usuario


async def obtener_usuarios(db: AsyncSession):
    result = await db.execute(select(models.Usuarios))
    return result.scalars().all()


async def crear_direcciones(db: AsyncSession, direccion: schemas.DireccionesEnvioCreateRequest):
    nueva_direccion = models.DireccionesEnvio(**direccion.dict())
    db.add(nueva_direccion)
    await db.commit()
    await db.refresh(nueva_direccion)

    result = await db.execute(select(models.DireccionesEnvio).options(selectinload(models.DireccionesEnvio.usuario)).where(models.DireccionesEnvio.id == nueva_direccion.id))

    direccion_con_relacion = result.scalar_one()
    return direccion_con_relacion


async def obtener_direcciones(db: AsyncSession):
    result = await db.execute(select(models.DireccionesEnvio).options(selectinload(models.DireccionesEnvio.usuario)))
    return result.scalars().all()