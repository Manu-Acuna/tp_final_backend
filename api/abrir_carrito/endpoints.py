from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.core.database import AsyncSessionLocal 
from api.productos import dal as productos_dal 
from api.core import models 
from . import dal, schemas 


router = APIRouter()

# Función para obtener la sesión de BD 
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def obtener_usuario_activo(db: AsyncSession = Depends(get_db)) -> models.Usuarios:
    # como ejemplo voy a agarrar el primer usuario, pero en realidad aca va la logica para obtener usuario desde un login
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
    # Podria volar este if y usar un front para avisar que el carrito esta vacio sin tirar error??
    if carrito is None:
        raise HTTPException(status_code=404, detail="Carrito vacio")
    return carrito


@router.get("/carrito/{id_del_carrito}/detalles") # Aca vá {id_del_carrito} el path parameter
async def ver_items_del_carrito(
    id_del_carrito: int, # FastAPI lo toma de la URL 
    db: AsyncSession = Depends(get_db)):
    # Aca paso el id_del_carrito a la función DAL
    detalles = await dal.obtener_detalle_carrito(db=db, carrito_id=id_del_carrito)
    if not detalles and not await dal.obtener_carrito_por_usuario_id(db=db, carrito_id=id_del_carrito): # Suponiendo que tienes una función para verificar si el carrito existe
         raise HTTPException(status_code=404, detail="Carrito no encontrado")
    return detalles


@router.post("/carrito/{id_del_carrito}/detalles", response_model=schemas.CarritoDetalleResponse)
async def agregar_item_al_carrito(
    id_del_carrito: int,
    item_data: schemas.AgregarItemAlCarritoRequest, # Usamos un esquema específico para añadir items
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuarios = Depends(obtener_usuario_activo)
):
    # Verifica que el carrito existe y pertenece al usuario autenticado
    carrito_usuario = await dal.obtener_carrito_por_usuario_id(db=db, user_id=current_user.id)
    if carrito_usuario is None or carrito_usuario.id != id_del_carrito:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este carrito o el carrito no existe")
    
    # Aca se obtiene información del producto para validar y obtener el precio
    producto = await productos_dal.obtener_producto_por_id(db=db, product_id=item_data.product_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    if producto.stock < item_data.quantity:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente para el producto {producto.name}. Stock disponible: {producto.stock}")
    
    # Se crea el CarritoDetalleCreateRequest con el precio del producto de la BD
    carrito_detalle_data = schemas.CarritoDetalleCreateRequest(
        quantity=item_data.quantity,
        price=producto.price, # Usar el precio del producto de la BD
        cart_id=id_del_carrito,
        product_id=item_data.product_id
    )

    # Llamar a la función DAL para crear el detalle del carrito
    db_carrito_detalle = await dal.crear_carrito_detalle(db=db, carrito_detalle=carrito_detalle_data)
    
    if db_carrito_detalle is None:
         raise HTTPException(status_code=500, detail="Error al agregar el item al carrito")

    return db_carrito_detalle


@router.delete("/carrito/{id_del_carrito}/detalles/{id_del_item}", status_code=204)
async def eliminar_item_del_carrito(id_del_carrito: int, id_del_item: int, db: AsyncSession = Depends(get_db), current_user: models.Usuarios = Depends(obtener_usuario_activo)):
    # Verificar que el carrito principal pertenece al usuario autenticado
    carrito_usuario = await dal.obtener_carrito_por_usuario_id(db=db, user_id=current_user.id)
    if carrito_usuario is None or carrito_usuario.id != id_del_carrito:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este carrito o el carrito no existe")
    # Obtener el item del carrito que se quiere eliminar
    item_a_eliminar = await dal.obtener_detalle_carrito_por_id(db=db, carrito_detalle_id=id_del_item)
    # Verificar que el item existe y pertenece al carrito especificado
    if item_a_eliminar is None or item_a_eliminar.cart_id != id_del_carrito:
        raise HTTPException(status_code=404, detail="Ítem no encontrado en este carrito")
    # Eliminar el ítem
    await dal.eliminar_item_del_carrito(db=db, carrito_detalle=item_a_eliminar)
    # No se devuelve contenido, por eso status_code=204 (No Content)
    return


@router.put("/carrito/{id_del_carrito}/detalles/{id_del_item}", response_model=schemas.CarritoDetalleResponse)
async def actualizar_cantidad_items_del_carrito(id_del_carrito: int, id_del_item: int, item_update_data: schemas.ActualizarCantidadCarritoRequest, db: AsyncSession = Depends(get_db), current_user: models.Usuarios = Depends(obtener_usuario_activo)):
    # Verificar que el carrito principal pertenece al usuario autenticado
    carrito_usuario = await dal.obtener_carrito_por_usuario_id(db=db, user_id=current_user.id)
    if carrito_usuario is None or carrito_usuario.id != id_del_carrito:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este carrito o el carrito no existe")
    
    # Obtener el detalle del carrito (el ítem) que se quiere actualizar
    item_a_actualizar = await dal.obtener_detalle_carrito_por_id(db=db, carrito_detalle_id=id_del_item)

    # Verificar que el ítem existe y pertenece al carrito especificado
    if item_a_actualizar is None or item_a_actualizar.cart_id != id_del_carrito:
        raise HTTPException(status_code=404, detail="Ítem no encontrado en este carrito")

    # Obtener información del producto para validar stock y obtener precio unitario
    producto = await productos_dal.obtener_producto_por_id(db=db, product_id=item_a_actualizar.product_id)
    if producto is None:
        # Esto sería raro si el item_a_actualizar existe, pero es una buena verificación
        raise HTTPException(status_code=404, detail="Producto asociado al ítem no encontrado")

    if item_update_data.quantity <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor que cero. Para eliminar el ítem, usa el endpoint DELETE.")

    if producto.stock < item_update_data.quantity:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente para el producto {producto.name}. Stock disponible: {producto.stock}")

    # Actualizar el ítem usando la función DAL
    db_carrito_detalle_actualizado = await dal.actualizar_cantidad_item_carrito(
        db=db, item_carrito=item_a_actualizar, nueva_cantidad=item_update_data.quantity, precio_unitario_producto=producto.price
    )
    return db_carrito_detalle_actualizado


@router.delete("/carrito/{id_del_carrito}/vaciar", status_code=204)
async def vaciar_carrito_del_usuario(id_del_carrito: int, db: AsyncSession = Depends(get_db), current_user: models.Usuarios = Depends(obtener_usuario_activo)):
    # Verifico que el carrito principal pertenece al usuario autenticado
    carrito_usuario = await dal.obtener_carrito_por_usuario_id(db=db, user_id=current_user.id)
    if carrito_usuario is None or carrito_usuario.id != id_del_carrito:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este carrito o el carrito no existe")

    # Aca se puede vaciar el carrito usando la función DAL
    await dal.vaciar_carrito_completo(db=db, carrito_id=id_del_carrito)
    return # No se devuelve contenido (status_code=204)