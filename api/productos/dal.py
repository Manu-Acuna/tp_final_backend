from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from api.core import models
from api.productos import schemas


async def crear_producto(db: AsyncSession, producto: schemas.ProductoCreateRequest):
    nuevo_producto = models.Productos(**producto.dict())
    db.add(nuevo_producto)
    await db.commit()
    await db.refresh(nuevo_producto)

    return nuevo_producto


async def obtener_productos(db: AsyncSession):
    result = await db.execute(select(models.Productos))
    return result.scalars().all()


async def crear_categoria(db: AsyncSession, categoria: schemas.CategoriaCreateRequest):
    nueva_categoria = models.Categorias(**categoria.dict())
    db.add(nueva_categoria)
    await db.commit()
    await db.refresh(nueva_categoria)

    result = await db.execute(select(models.Categorias).options(selectinload(models.Categorias.producto)).where(models.Categorias.id == nueva_categoria.id))

    categoria_con_relacion = result.scalar_one()
    return categoria_con_relacion


async def obtener_categorias(db: AsyncSession):
    result = await db.execute(select(models.Categorias).options(selectinload(models.Categorias.producto)))
    return result.scalars().all()