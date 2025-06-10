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


async def crear_rol(db: AsyncSession, rol: schemas.RolesCreateRequest):
    nuevo_rol = models.Roles(**rol.dict())
    db.add(nuevo_rol)
    await db.commit()
    await db.refresh(nuevo_rol)

    result = await db.execute(select(models.Roles).options(selectinload(models.Roles.usuarios)).where(models.Roles.id == nuevo_rol.id))
    rol_con_relacion = result.scalar_one()
    return rol_con_relacion


async def obtener_usuarios(db: AsyncSession):
    result = await db.execute(select(models.Usuarios))
    return result.scalars().all()


async def obtener_roles(db: AsyncSession):
    result = await db.execute(select(models.Roles).options(selectinload(models.Roles.usuarios)))
    return result.scalars().all()













