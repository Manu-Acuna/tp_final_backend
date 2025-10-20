from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from api.core.database import AsyncSessionLocal
from api.auth.endpoints import get_current_user
from api.core import models
from . import dal, schemas

router = APIRouter(
    prefix="/users", # Cambiado a 'users' para coincidir con el frontend
    tags=["Usuarios"]
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/me/", response_model=schemas.User, summary="Obtener perfil del usuario actual")
async def read_users_me(current_user: models.Usuarios = Depends(get_current_user)):
    return current_user

@router.put("/me/", response_model=schemas.User, summary="Actualizar perfil del usuario actual")
async def update_current_user(
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuarios = Depends(get_current_user)
):
    if not user_update.nombre and not user_update.apellido:
        raise HTTPException(status_code=400, detail="Se requiere al menos un campo (nombre o apellido) para actualizar.")

    # 1. Obtenemos una instancia del usuario en la sesión actual del endpoint.
    db_user = await db.get(models.Usuarios, current_user.id)
    if not db_user:
        # Esto es una salvaguarda, no debería ocurrir con un token válido.
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 2. Actualizamos los datos y guardamos.
    db_user.nombre = user_update.nombre if user_update.nombre is not None else db_user.nombre
    db_user.apellido = user_update.apellido if user_update.apellido is not None else db_user.apellido
    await db.commit()

    # 3. En lugar de devolver el objeto SQLAlchemy, construimos manualmente un diccionario
    #    o un objeto Pydantic para asegurar que todos los campos estén presentes.
    #    Esto evita cualquier problema con el estado del objeto SQLAlchemy después del commit.
    return {
        "id": db_user.id,
        "email": db_user.email,
        "nombre": db_user.nombre,
        "apellido": db_user.apellido,
        "is_admin": db_user.is_admin,
        "fecha_nacimiento": db_user.fecha_nacimiento
    }

@router.post("/me/direcciones", response_model=schemas.DireccionEnvioResponse, status_code=status.HTTP_201_CREATED, summary="Crear una nueva dirección de envío para el usuario actual")
async def crear_direccion_para_usuario_actual(
    direccion: schemas.DireccionEnvioCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuarios = Depends(get_current_user)
):
    return await dal.crear_direccion_envio(db=db, direccion=direccion, user_id=current_user.id)

@router.get("/me/direcciones", response_model=List[schemas.DireccionEnvioResponse], summary="Listar las direcciones de envío del usuario actual")
async def listar_direcciones_del_usuario_actual(
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuarios = Depends(get_current_user)
):
    return await dal.obtener_direcciones_por_usuario(db=db, user_id=current_user.id)