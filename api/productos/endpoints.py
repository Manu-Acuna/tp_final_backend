from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from api.core.database import get_db # Importamos get_db desde un lugar central
from api.core import models
from api.auth.endpoints import get_current_admin_user # Importamos la dependencia de admin
from . import dal, schemas

router = APIRouter()

@router.get("/productos/", response_model=List[schemas.ProductoResponse], summary="Obtener todos los productos", tags=["Productos"])
async def listar_productos(db: AsyncSession = Depends(get_db)):
    return await dal.obtener_productos(db=db)

@router.get("/productos/{product_id}", response_model=schemas.ProductoResponse, summary="Obtener un producto por su ID", tags=["Productos"])
async def obtener_producto(product_id: int, db: AsyncSession = Depends(get_db)):
    producto = await dal.obtener_producto_por_id(db=db, product_id=product_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

# Filtrar productos por categoría
@router.get("/productos/categoria/{categoria_id}", response_model=List[schemas.ProductoResponse], summary="Obtener productos por categoría", tags=["Productos"])
async def obtener_productos_por_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    productos = await dal.obtener_productos_por_categoria(db=db, categoria_id=categoria_id)
    return productos

@router.get("/productos/buscar/", response_model=List[schemas.ProductoResponse], summary="Buscar productos por nombre o descripción", tags=["Productos"])
async def buscar_productos(query: str, db: AsyncSession = Depends(get_db)):
    """
    Busca productos que coincidan con el término de búsqueda (query)
    en su nombre o descripción.
    """
    productos_encontrados = await dal.buscar_productos_por_termino(db=db, termino=query)
    if not productos_encontrados:
        return [] # Devuelve una lista vacía si no hay resultados
    return productos_encontrados

# --- Endpoints de Categorías ---

@router.post("/categorias/", response_model=schemas.CategoriaResponse, status_code=201, tags=["Categorías"])
async def crear_categoria(categoria: schemas.CategoriaCreateRequest, db: AsyncSession = Depends(get_db)):
    db_categoria = await dal.crear_categoria(db=db, categoria=categoria)
    return db_categoria

@router.get("/categorias/", response_model=List[schemas.CategoriaResponse], tags=["Categorías"])
async def listar_categorias(db: AsyncSession = Depends(get_db)):
    categorias = await dal.obtener_categorias(db=db)
    return categorias

@router.get("/categorias/{categoria_id}", response_model=schemas.CategoriaResponse, tags=["Categorías"])
async def obtener_categoria_por_id(categoria_id: int, db: AsyncSession = Depends(get_db)):
    db_categoria = await dal.obtener_categoria_por_id(db=db, categoria_id=categoria_id)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return db_categoria

@router.put("/categorias/{categoria_id}", response_model=schemas.CategoriaResponse, tags=["Categorías"])
async def actualizar_categoria(categoria_id: int, categoria: schemas.CategoriaCreateRequest, db: AsyncSession = Depends(get_db)):
    db_categoria = await dal.actualizar_categoria(db=db, categoria_id=categoria_id, categoria=categoria)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return db_categoria

@router.delete("/categorias/{categoria_id}",status_code=204, tags=["Categorías"])
async def eliminar_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    eliminado = await dal.eliminar_categoria(db=db, categoria_id=categoria_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return None

# --- Endpoints de Admin para Productos ---

@router.post("/admin/productos/", response_model=schemas.ProductoResponse, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo producto (Admin)", tags=["Admin"])
async def crear_producto(
    producto: schemas.ProductoCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: models.Usuarios = Depends(get_current_admin_user)
):
    return await dal.crear_producto(db=db, producto=producto)

@router.put("/admin/productos/{product_id}", response_model=schemas.ProductoResponse, summary="Actualizar un producto (Admin)", tags=["Admin"])
async def actualizar_producto(
    product_id: int,
    producto: schemas.ProductoCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: models.Usuarios = Depends(get_current_admin_user)
):
    db_producto = await dal.actualizar_producto(db=db, product_id=product_id, producto=producto)
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_producto

@router.patch("/admin/productos/{product_id}", response_model=schemas.ProductoResponse, summary="Actualizar parcialmente un producto (Admin)", tags=["Admin"])
async def actualizar_parcial_producto(
    product_id: int, 
    producto: schemas.ProductoUpdateRequest, 
    db: AsyncSession = Depends(get_db), 
    current_admin: models.Usuarios = Depends(get_current_admin_user)
):
    db_producto = await dal.actualizar_parcialmente_producto(db=db, product_id=product_id, producto=producto)
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_producto

@router.delete("/admin/productos/{product_id}",status_code=204, summary="Eliminar un producto (Admin)", tags=["Admin"])
async def eliminar_producto(
    product_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_admin: models.Usuarios = Depends(get_current_admin_user)
):
    eliminado = await dal.eliminar_producto(db=db, product_id=product_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return None