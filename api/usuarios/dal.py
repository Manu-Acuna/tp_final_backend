from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from api.core import models
from api.usuarios import schemas


async def crear_usuario(db: AsyncSession, usuario: schemas.UsuariosCreateRequest):
    nuevo_usuario = models.Usuarios(**usuario.dict())
    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)

    return nuevo_usuario


async def obtener_usuarios(db: AsyncSession):
    result = await db.execute(select(models.Usuarios))
    return result.scalars().all()














