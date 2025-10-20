from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.core import models
from . import schemas, security


async def get_user_by_email(db: AsyncSession, email: str):
    """Busca un usuario por su email."""
    query = select(models.Usuarios).where(models.Usuarios.email == email)
    result = await db.execute(query)
    return result.scalars().first()


async def authenticate_user(db: AsyncSession, email: str, password: str):
    """
    Autentica a un usuario. Devuelve el objeto de usuario si es exitoso, si no None.
    """
    user = await get_user_by_email(db, email)
    if not user or not security.verify_password(password, user.password):
        return None
    return user


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    """Crea un nuevo usuario en la base de datos."""
    hashed_password = security.get_password_hash(user.password)
    db_user = models.Usuarios(
        email=user.email,
        password=hashed_password,
        nombre=user.nombre,
        apellido=user.apellido,
        fecha_nacimiento=user.fecha_nacimiento
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Obtiene una lista de usuarios."""
    result = await db.execute(select(models.Usuarios).offset(skip).limit(limit))
    return result.scalars().all()
