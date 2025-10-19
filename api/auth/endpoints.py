from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from jose import JWTError, jwt

from api.core.database import get_db # <-- CAMBIO IMPORTANTE
from api.core import models
from . import dal, schemas, security

# --- CONFIGURACIÓN DE AUTENTICACIÓN ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
router = APIRouter()

# --- DEPENDENCIAS DE AUTENTICACIÓN ---
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await dal.get_user_by_email(db, email=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user: models.Usuarios = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos de administrador")
    return current_user

# --- ENDPOINTS ---
@router.post("/token", response_model=schemas.Token, tags=["Autenticación"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await dal.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Autenticación"])
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await dal.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    return await dal.create_user(db=db, user=user)

@router.get("/users/me/", response_model=schemas.UserResponse, tags=["Usuarios"])
async def read_users_me(current_user: models.Usuarios = Depends(get_current_user)):
    return current_user

@router.get("/users/", response_model=List[schemas.UserResponse], tags=["Admin"])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), admin: models.Usuarios = Depends(get_current_admin_user)):
    users = await dal.get_users(db, skip=skip, limit=limit)
    return users
