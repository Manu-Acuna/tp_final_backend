from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.core import models
from . import schemas, security


async def get_user_by_username(db: AsyncSession, username: str):
    """Busca un usuario por su username o email."""
    # Permite iniciar sesión con email o username
    if '@' in username:
        query = select(models.Usuarios).where(models.Usuarios.email == username)
    else:
        query = select(models.Usuarios).where(models.Usuarios.username == username)
    result = await db.execute(query)
    return result.scalars().first()


async def authenticate_user(db: AsyncSession, username: str, password: str):
    """Autentica un usuario. Devuelve el usuario si es válido, si no False."""
    user = await get_user_by_username(db, username)
    if not user:
        return False
    if not security.verify_password(password, user.password):
        return False
    return user


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    """Crea un nuevo usuario en la base de datos."""
    hashed_password = security.get_password_hash(user.password)
    db_user = models.Usuarios(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

