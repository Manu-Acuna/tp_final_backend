from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.core.database import AsyncSessionLocal 
from api.core import models
from . import dal, schemas
import os
import uuid
import aiofiles


UPLOAD_DIRECTORY = "public/images/productos"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True) # Crea el directorio si no existe

router = APIRouter()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

#Funciona
@router.post("/productos/", response_model=schemas.ProductoResponse, status_code=201, tags=["productos"])
async def crear_producto(producto: schemas.ProductoCreateRequest, db: AsyncSession = Depends(get_db)):
    db_producto = await dal.crear_producto(db=db, producto=producto)
    return db_producto

#Funciona
@router.get("/productos/", response_model=list[schemas.ProductoResponse], tags=["productos"])
async def listar_productos(db: AsyncSession = Depends(get_db)):
    productos = await dal.obtener_productos(db=db)
    return productos

#Funciona
@router.get("/productos/{product_id}", response_model=schemas.ProductoResponse, tags=["productos"])
async def obtener_producto(product_id: int, db: AsyncSession = Depends(get_db)):
    producto = await dal.obtener_producto_por_id(db=db, product_id=product_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

#Funciona
@router.put("/productos/{product_id}", response_model=schemas.ProductoResponse, tags=["productos"])
async def actualizar_producto(product_id: int, producto: schemas.ProductoCreateRequest, db: AsyncSession = Depends(get_db)):
    db_producto = await dal.actualizar_producto(db=db, product_id=product_id, producto=producto)
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_producto


#Funciona
@router.patch("/productos/{product_id}", response_model=schemas.ProductoResponse, tags=["productos"])
async def actualizar_parcial_producto(product_id: int, producto: schemas.ProductoUpdateRequest, db: AsyncSession = Depends(get_db)):
    db_producto = await dal.actualizar_parcialmente_producto(db=db, product_id=product_id, producto=producto)
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_producto


#Funciona
@router.delete("/productos/{product_id}",status_code=204, tags=["productos"])
async def eliminar_producto(product_id: int, db: AsyncSession = Depends(get_db)):
    eliminado = await dal.eliminar_producto(db=db, product_id=product_id)
    if not eliminado: 
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return None

#Funciona
@router.post("/categorias/", response_model=schemas.CategoriaResponse, status_code=201, tags=["categorias"])
async def crear_categoria(categoria: schemas.CategoriaCreateRequest, db: AsyncSession = Depends(get_db)):
    db_categoria = await dal.crear_categoria(db=db, categoria=categoria)
    return db_categoria

#Funciona
@router.get("/categorias/", response_model=list[schemas.CategoriaResponse], tags=["categorias"])
async def listar_categorias(db: AsyncSession = Depends(get_db)):
    categorias = await dal.obtener_categorias(db=db)
    return categorias

#Funciona
@router.get("/categorias/{categoria_id}", response_model=schemas.CategoriaResponse, tags=["categorias"])
async def obtener_categoria_por_id(categoria_id: int, db: AsyncSession = Depends(get_db)):
    db_categoria = await dal.obtener_categoria_por_id(db=db, categoria_id=categoria_id)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return db_categoria

#Funciona
@router.put("/categorias/{categoria_id}", response_model=schemas.CategoriaResponse, tags=["categorias"])
async def actualizar_categoria(categoria_id: int, categoria: schemas.CategoriaCreateRequest, db: AsyncSession = Depends(get_db)):
    db_categoria = await dal.actualizar_categoria(db=db, categoria_id=categoria_id, categoria=categoria)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return db_categoria

#Funciona
@router.delete("/categorias/{categoria_id}",status_code=204, tags=["categorias"])
async def eliminar_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    eliminado = await dal.eliminar_categoria(db=db, categoria_id=categoria_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return None
