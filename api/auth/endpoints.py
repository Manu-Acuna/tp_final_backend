from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.core import models
from api.productos.endpoints import get_db
from . import dal, schemas, security

router = APIRouter()


async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    """
    Dependencia para obtener el usuario actual a partir del token JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=email) # El schema espera 'username', pero le pasamos el email
    except security.JWTError:
        raise credentials_exception
    user = await dal.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user: models.Usuarios = Depends(get_current_user)):
    """
    Dependencia que verifica si el usuario actual es un administrador.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: se requieren privilegios de administrador.")
    return current_user


@router.post("/register", response_model=schemas.UserResponse, status_code=201, tags=["auth"])
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await dal.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user_email = await dal.get_user_by_username(db, username=user.email)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await dal.create_user(db=db, user=user)


@router.post("/token", response_model=schemas.Token, tags=["auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await dal.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=schemas.UserResponse, tags=["auth"])
async def read_users_me(current_user: models.Usuarios = Depends(get_current_user)):
    return current_user
