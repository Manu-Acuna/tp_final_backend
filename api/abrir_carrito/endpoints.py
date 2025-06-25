from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.core.database import AsyncSessionLocal 
from api.productos import dal as productos_dal 
from api.core import models 
from . import dal, schemas 


router = APIRouter()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def obtener_usuario_activo(db: AsyncSession = Depends(get_db)) -> models.Usuarios:
    user = await db.execute(select(models.Usuarios))
    current_user = user.scalars().first()
    if not current_user:
        raise HTTPException(status_code=401, detail="Usuario no autenticado")
    return current_user


@router.post("/carrito", response_model=schemas.CarritoResponse)
async def crear_carrito(
    carrito_data: schemas.CarritoCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuarios = Depends(obtener_usuario_activo)
):
    if carrito_data.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear un carrito para este usuario")
    
    db_carrito = await dal.crear_carrito(db=db, carrito=carrito_data)
    if db_carrito is None:
        raise HTTPException(status_code=400, detail="Error al crear el carrito")
    return db_carrito


@router.get("/carrito/{id_del_carrito}", response_model=schemas.CarritoResponse)
async def ver_carrito(
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuarios = Depends(obtener_usuario_activo)
):
    carrito = await dal.obtener_carrito_por_usuario_id(db=db, user_id=current_user.id)
    if carrito is None:
        raise HTTPException(status_code=404, detail="Carrito vacio")
    return carrito


@router.get("/carrito/{id_del_carrito}/detalles") 
async def ver_items_del_carrito(
    id_del_carrito: int, 
    db: AsyncSession = Depends(get_db)):
    detalles = await dal.obtener_detalle_carrito(db=db, carrito_id=id_del_carrito)
    if not detalles and not await dal.obtener_carrito_por_usuario_id(db=db, carrito_id=id_del_carrito): 
         raise HTTPException(status_code=404, detail="Carrito no encontrado")
    return detalles


@router.post("/carrito/{id_del_carrito}/detalles", response_model=schemas.CarritoDetalleResponse)
async def agregar_item_al_carrito(
    id_del_carrito: int,
    item_data: schemas.AgregarItemAlCarritoRequest, 
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuarios = Depends(obtener_usuario_activo)
):
    
    carrito_usuario = await dal.obtener_carrito_por_usuario_id(db=db, user_id=current_user.id)
    if carrito_usuario is None or carrito_usuario.id != id_del_carrito:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este carrito o el carrito no existe")
    
    
    producto = await productos_dal.obtener_producto_por_id(db=db, product_id=item_data.product_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    if producto.stock < item_data.quantity:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente para el producto {producto.name}. Stock disponible: {producto.stock}")
    
    carrito_detalle_data = schemas.CarritoDetalleCreateRequest(
        quantity=item_data.quantity,
        price=producto.price, 
        cart_id=id_del_carrito,
        product_id=item_data.product_id
    )

    db_carrito_detalle = await dal.crear_carrito_detalle(db=db, carrito_detalle=carrito_detalle_data)
    
    if db_carrito_detalle is None:
         raise HTTPException(status_code=500, detail="Error al agregar el item al carrito")

    return db_carrito_detalle


@router.delete("/carrito/{id_del_carrito}/detalles/{id_del_item}", status_code=204)
async def eliminar_item_del_carrito(id_del_carrito: int, id_del_item: int, db: AsyncSession = Depends(get_db), current_user: models.Usuarios = Depends(obtener_usuario_activo)):
    carrito_usuario = await dal.obtener_carrito_por_usuario_id(db=db, user_id=current_user.id)
    if carrito_usuario is None or carrito_usuario.id != id_del_carrito:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este carrito o el carrito no existe")
    
    item_a_eliminar = await dal.obtener_detalle_carrito_por_id(db=db, carrito_detalle_id=id_del_item)
    
    if item_a_eliminar is None or item_a_eliminar.cart_id != id_del_carrito:
        raise HTTPException(status_code=404, detail="Ítem no encontrado en este carrito")
    
    await dal.eliminar_item_del_carrito(db=db, carrito_detalle=item_a_eliminar)
    
    return


@router.put("/carrito/{id_del_carrito}/detalles/{id_del_item}", response_model=schemas.CarritoDetalleResponse)
async def actualizar_cantidad_items_del_carrito(id_del_carrito: int, id_del_item: int, item_update_data: schemas.ActualizarCantidadCarritoRequest, db: AsyncSession = Depends(get_db), current_user: models.Usuarios = Depends(obtener_usuario_activo)):
    
    carrito_usuario = await dal.obtener_carrito_por_usuario_id(db=db, user_id=current_user.id)
    if carrito_usuario is None or carrito_usuario.id != id_del_carrito:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este carrito o el carrito no existe")
    
    item_a_actualizar = await dal.obtener_detalle_carrito_por_id(db=db, carrito_detalle_id=id_del_item)

    if item_a_actualizar is None or item_a_actualizar.cart_id != id_del_carrito:
        raise HTTPException(status_code=404, detail="Ítem no encontrado en este carrito")

    producto = await productos_dal.obtener_producto_por_id(db=db, product_id=item_a_actualizar.product_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto asociado al ítem no encontrado")

    if item_update_data.quantity <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor que cero. Para eliminar el ítem, usa el endpoint DELETE.")

    if producto.stock < item_update_data.quantity:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente para el producto {producto.name}. Stock disponible: {producto.stock}")

    db_carrito_detalle_actualizado = await dal.actualizar_cantidad_item_carrito(
        db=db, item_carrito=item_a_actualizar, nueva_cantidad=item_update_data.quantity, precio_unitario_producto=producto.price
    )
    return db_carrito_detalle_actualizado


@router.delete("/carrito/{id_del_carrito}/vaciar", status_code=204)
async def vaciar_carrito_del_usuario(id_del_carrito: int, db: AsyncSession = Depends(get_db), current_user: models.Usuarios = Depends(obtener_usuario_activo)):
    carrito_usuario = await dal.obtener_carrito_por_usuario_id(db=db, user_id=current_user.id)
    if carrito_usuario is None or carrito_usuario.id != id_del_carrito:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este carrito o el carrito no existe")

    await dal.vaciar_carrito_completo(db=db, carrito_id=id_del_carrito)
    return 