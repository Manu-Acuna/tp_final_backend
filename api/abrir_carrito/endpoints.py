from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from sqlalchemy.future import select
from api.core.database import AsyncSessionLocal
from api.auth.endpoints import get_current_user
from api.productos import dal as productos_dal
from api.core import models, dal as core_dal
from api.core.enum import PedidoStatus, PagoStatus
from . import dal, schemas 


router = APIRouter()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/carrito/mi_carrito", response_model=schemas.CarritoResponse, summary="Obtener o crear el carrito del usuario activo", description="Recupera el carrito activo del usuario, Si no existe, lo crea y lo devuelve.", tags=["Carrito"])
async def obtener_o_crear_carrito_usuario(db: AsyncSession = Depends(get_db), current_user: models.Usuarios = Depends(get_current_user)):
    db_carrito = await dal.obtener_o_crear_carrito(db=db, user_id=current_user.id)
    if db_carrito is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo obtener el carrito.")
    return db_carrito


@router.get("/carrito/mi_carrito/total", response_model=schemas.CarritoTotalResponse, summary="Obtener el total del carrito del usuario", description="Obtiene el total del carrito del usuario", tags=["Carrito"])
async def obtener_total_carrito(db: AsyncSession = Depends(get_db), current_user: models.Usuarios = Depends(get_current_user)):
    carrito = await dal.obtener_o_crear_carrito(db=db, user_id=current_user.id)
    total = await dal.calcular_total_carrito(db=db, carrito_id=carrito.id)
    return schemas.CarritoTotalResponse(cart_id=carrito.id, total_price=total)


@router.get("/carrito/mi_carrito/detalles", response_model=list[schemas.CarritoDetalleResponse], summary="Ver todos los items en el carrito del usuario", tags=["Carrito"]) 
async def ver_items_del_carrito(db: AsyncSession = Depends(get_db), current_user: models.Usuarios = Depends(get_current_user)):
    carrito = await dal.obtener_o_crear_carrito(db=db, user_id=current_user.id)
    if not carrito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")

    detalles_db = await dal.obtener_detalle_carrito(db=db, carrito_id=carrito.id)

    response_detalles = []
    for detalle in detalles_db:
        producto = await productos_dal.obtener_producto_por_id(db=db, product_id=detalle.product_id)

        item_con_nombre = {
            "id": detalle.id,
            "cart_id": detalle.cart_id,
            "product_id": detalle.product_id,
            "quantity": detalle.quantity,
            "price": detalle.price,
            "product_name": producto.name if producto else "Nombre no disponible",
            "image_url": producto.image_url if producto else None #Aca incluyo la URL de la imagen
        }
        response_detalles.append(item_con_nombre)

    return response_detalles

@router.post("/carrito/mi_carrito/detalles", response_model=schemas.CarritoDetalleResponse, status_code=status.HTTP_201_CREATED, summary="Agregar un item al carrito (o actualizar la cantidad)", tags=["Carrito"])
async def agregar_item_al_carrito(
    item_data: schemas.AgregarItemAlCarritoRequest, db: AsyncSession = Depends(get_db), current_user: models.Usuarios = Depends(get_current_user)):
    
    carrito = await dal.obtener_o_crear_carrito(db=db, user_id=current_user.id)
    if not carrito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")
    
    producto = await productos_dal.obtener_producto_por_id(db=db, product_id=item_data.product_id)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    
    #Arreglo un bug en el que puedo agregar mas productos al carrito de los que tengo en stock
    result = await db.execute(select(models.CarritoDetalle).where(models.CarritoDetalle.cart_id == carrito.id, models.CarritoDetalle.product_id == item_data.product_id))

    item_existente = result.scalars().first()
    
    cantidad_actual_en_carrito = item_existente.quantity if item_existente else 0

    #Aca hacemos la validacion

    if producto.stock < (cantidad_actual_en_carrito + item_data.quantity):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Stock insuficiente para el producto {producto.name}. Stock disponible: {producto.stock}")
    
    #Fin de la validacion y seguimos con la logica

    db_carrito_detalle = await dal.agregar_item_al_carrito(
        db=db, 
        cart_id=carrito.id, 
        product_id=item_data.product_id, 
        quantity=item_data.quantity, 
        price=producto.price
    )
    
    if db_carrito_detalle is None:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al agregar el item al carrito")

    # Construimos la respuesta para que coincida con el response_model, incluyendo el nombre del producto.
    return {
        "id": db_carrito_detalle.id,
        "cart_id": db_carrito_detalle.cart_id,
        "product_id": db_carrito_detalle.product_id,
        "quantity": db_carrito_detalle.quantity,
        "price": db_carrito_detalle.price,
        "product_name": producto.name,
        "image_url": producto.image_url # Añadimos la URL de la imagen
    }


@router.delete("/carrito/mi_carrito/detalles/{id_del_item}", status_code=204, summary="Eliminar un item del carrito del usuario", tags=["Carrito"])
async def eliminar_item_del_carrito(id_del_item: int, db: AsyncSession = Depends(get_db), current_user: models.Usuarios = Depends(get_current_user)):
    carrito_usuario = await dal.obtener_o_crear_carrito(db=db, user_id=current_user.id)
    id_del_carrito = carrito_usuario.id
    if not carrito_usuario or carrito_usuario.id != id_del_carrito:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para modificar este carrito o el carrito no existe")
    
    item_a_eliminar = await dal.obtener_detalle_carrito_por_id(db=db, carrito_detalle_id=id_del_item)
    
    if not item_a_eliminar or item_a_eliminar.cart_id != id_del_carrito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ítem no encontrado en este carrito")
    
    await dal.eliminar_item_del_carrito(db=db, carrito_detalle=item_a_eliminar)
    
    return


@router.put("/carrito/mi_carrito/detalles/{id_del_item}", response_model=schemas.CarritoDetalleResponse, summary="Actualizar la cantidad de un item en el carrito", tags=["Carrito"])
async def actualizar_cantidad_items_del_carrito(id_del_item: int, item_update_data: schemas.ActualizarCantidadCarritoRequest, db: AsyncSession = Depends(get_db), current_user: models.Usuarios = Depends(get_current_user)):
    carrito_usuario = await dal.obtener_o_crear_carrito(db=db, user_id=current_user.id)
    id_del_carrito = carrito_usuario.id
    if not carrito_usuario or carrito_usuario.id != id_del_carrito:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para modificar este carrito o el carrito no existe")
    
    item_a_actualizar = await dal.obtener_detalle_carrito_por_id(db=db, carrito_detalle_id=id_del_item)

    if not item_a_actualizar or item_a_actualizar.cart_id != id_del_carrito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ítem no encontrado en este carrito")

    producto = await productos_dal.obtener_producto_por_id(db=db, product_id=item_a_actualizar.product_id)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto asociado al ítem no encontrado")

    if item_update_data.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La cantidad debe ser mayor que cero. Para eliminar el ítem, usa el endpoint DELETE.")

    if producto.stock < item_update_data.quantity:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente para el producto {producto.name}. Stock disponible: {producto.stock}")

    db_carrito_detalle_actualizado = await dal.actualizar_cantidad_item_carrito(
        db=db, carrito_detalle=item_a_actualizar, nueva_cantidad=item_update_data.quantity, precio_unitario_producto=producto.price
    )

    # Construimos la respuesta para que coincida con el response_model, incluyendo el nombre y la imagen del producto.
    return {
        "id": db_carrito_detalle_actualizado.id,
        "cart_id": db_carrito_detalle_actualizado.cart_id,
        "product_id": db_carrito_detalle_actualizado.product_id,
        "quantity": db_carrito_detalle_actualizado.quantity,
        "price": db_carrito_detalle_actualizado.price,
        "product_name": producto.name, # Usamos el producto que ya obtuvimos
        "image_url": producto.image_url # Usamos el producto que ya obtuvimos
    }


@router.delete("/carrito/mi_carrito/vaciar", status_code=status.HTTP_204_NO_CONTENT, summary="Vaciar el carrito del usuario", tags=["Carrito"])
async def vaciar_carrito_del_usuario(db: AsyncSession = Depends(get_db), current_user: models.Usuarios = Depends(get_current_user)):
    carrito_usuario = await dal.obtener_o_crear_carrito(db=db, user_id=current_user.id)
    id_del_carrito = carrito_usuario.id
    if not carrito_usuario or carrito_usuario.id != id_del_carrito:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para modificar este carrito o el carrito no existe")

    await dal.vaciar_carrito_completo(db=db, carrito_id=id_del_carrito)
    return 


@router.post("/pagos/crear_preferencia", response_model=schemas.PreferenciaPagoResponse, summary="Crear una preferencia de pago", tags=["Pagos"])
async def crear_preferencia_pago(
    request_data: schemas.FinalizarCompraRequest,
    db: AsyncSession = Depends(get_db), 
    current_user: models.Usuarios = Depends(get_current_user)
):
    """
    Simula la creación de una preferencia de pago en una pasarela externa.
    Valida el carrito y el stock, y si todo está OK, devuelve una URL a una
    página de pago simulada.
    """
    carrito = await dal.obtener_o_crear_carrito(db=db, user_id=current_user.id)
    items_carrito = await dal.obtener_detalle_carrito(db=db, carrito_id=carrito.id)

    if not items_carrito:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El carrito está vacío.")

    for item in items_carrito:
        producto = await productos_dal.obtener_producto_por_id(db=db, product_id=item.product_id)
        if not producto or producto.stock < item.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Stock insuficiente para {producto.name if producto else 'un producto'}.")

    # En un caso real, aquí se interactuaría con la API de MercadoPago/Stripe.
    # Para simular, creamos una URL a una página de pago ficticia.
    # Devolvemos una ruta relativa que el frontend usará para redirigir.
    redirect_url = f"pago_simulado.html?user_id={current_user.id}&address_id={request_data.address_id}"
    
    return {"redirect_url": redirect_url}