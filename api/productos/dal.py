from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from api.core import models
from typing import Optional
from api.productos import schemas
from sqlalchemy import or_


async def crear_producto(db: AsyncSession, producto: schemas.ProductoCreateRequest):
    nuevo_producto = models.Productos(**producto.dict())
    db.add(nuevo_producto)
    await db.commit()
    await db.refresh(nuevo_producto)

    return nuevo_producto


async def obtener_productos(db: AsyncSession):
    result = await db.execute(select(models.Productos))
    
    return result.scalars().all()


async def obtener_producto_por_id(db: AsyncSession, product_id: int):
    query = select(models.Productos).where(models.Productos.id == product_id)
    result = await db.execute(query)
    
    return result.scalars().first()


async def obtener_producto_por_nombre(db: AsyncSession, nombre: str) -> Optional[models.Productos]:
    result = await db.execute(
        select(models.Productos).where(models.Productos.name == nombre))
    return result.scalars().first()

# Obtener productos por categoría
async def obtener_productos_por_categoria(db: AsyncSession, categoria_id: int):
    query = select(models.Productos).where(models.Productos.category_id == categoria_id)
    result = await db.execute(query)
    
    return result.scalars().all()

async def actualizar_producto(db: AsyncSession, product_id: int, producto: schemas.ProductoCreateRequest):
    db_producto = await db.get(models.Productos, product_id)
    if db_producto:
        update_data = producto.dict()
        for key, value in update_data.items():
            setattr(db_producto, key, value)
        await db.commit()
        await db.refresh(db_producto)
    return db_producto


async def actualizar_parcialmente_producto(db: AsyncSession, product_id: int, producto: schemas.ProductoUpdateRequest):
    db_producto = await db.get(models.Productos, product_id)
    if db_producto:
        update_data = producto.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_producto, key, value)
        await db.commit()
        await db.refresh(db_producto)
    return db_producto


async def eliminar_producto(db: AsyncSession, product_id: int):
    db_producto = await db.get(models.Productos, product_id)
    if db_producto:
        await db.delete(db_producto)
        await db.commit()
        return True
    return False


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


async def obtener_categoria_por_id(db: AsyncSession, categoria_id: int):
    query = select(models.Categorias).where(models.Categorias.id == categoria_id)
    result = await db.execute(query)
    
    return result.scalars().first()


async def actualizar_categoria(db: AsyncSession, categoria_id: int, categoria: schemas.CategoriaCreateRequest):
    db_categoria = await db.get(models.Categorias, categoria_id)
    if db_categoria:
        db_categoria.name = categoria.name
        await db.commit()
        await db.refresh(db_categoria)
    
    return db_categoria


async def eliminar_categoria(db: AsyncSession, categoria_id: int):
    db_categoria = await db.get(models.Categorias, categoria_id)
    if db_categoria:
        await db.delete(db_categoria)
        await db.commit()
        return True
    
    return False

async def buscar_productos_por_termino(db: AsyncSession, termino: str):
    # Usamos ilike para una búsqueda case-insensitive (ignora mayúsculas/minúsculas)
    termino_like = f"%{termino}%"
    result = await db.execute(
        select(models.Productos)
        .where(
            or_(
                models.Productos.name.ilike(termino_like),
                models.Productos.description.ilike(termino_like)
            )
        )
    )
    return result.scalars().all()