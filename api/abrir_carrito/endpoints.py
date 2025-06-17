# Ejemplo en api/abrir_carrito/endpoints.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.core.database import AsyncSessionLocal # Asumiendo que tienes get_db
from api.core import models # tu modelo
from . import dal, schemas # tu archivo dal.py
# from . import schemas # tus esquemas de respuesta


router = APIRouter()

# Función para obtener la sesión de BD (deberías tener una similar)
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
async def leer_carrito(
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuarios = Depends(obtener_usuario_activo)
):
    carrito = await dal.obtener_carrito_por_usuario_id(db=db, user_id=current_user.id)
    # Podria volar este if y usar un front para avisar que el carrito esta vacio sin tirar error
    if carrito is None:
        raise HTTPException(status_code=404, detail="Carrito vacio")
    return carrito


@router.get("/carrito/{id_del_carrito}/detalles") # Aca vá {id_del_carrito} el path parameter
async def leer_detalles_de_un_carrito(
    id_del_carrito: int, # FastAPI lo toma de la URL 
    db: AsyncSession = Depends(get_db)):
    # Aquí pasas el id_del_carrito a tu función DAL
    detalles = await dal.obtener_detalle_carrito(db=db, carrito_id=id_del_carrito)
    if not detalles and not await dal.obtener_carrito_por_usuario_id(db=db, carrito_id=id_del_carrito): # Suponiendo que tienes una función para verificar si el carrito existe
         raise HTTPException(status_code=404, detail="Carrito no encontrado")
    return detalles
