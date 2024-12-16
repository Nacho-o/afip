import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import User as UserModel
from app.schemas import UserCreate, User as UserSchema

router = APIRouter()

@router.post("/users/", response_model=UserSchema)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Verificar si el email o el username ya existen
    stmt = select(UserModel).where(
        (UserModel.email == user.email) | (UserModel.username == user.username)
    )
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        elif existing_user.username == user.username:
            raise HTTPException(status_code=400, detail="Username already registered")

    # Crear un nuevo usuario
    db_user = UserModel(
        username=user.username,
        password_hash=user.password_hash,
        email=user.email,
        cuit=user.cuit,
        full_name=user.full_name,
        is_active=True,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return UserSchema.model_validate(db_user)

@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    # Consulta para buscar al usuario por su ID
    stmt = (
        select(UserModel)
        .options(selectinload(UserModel.certificates))  # Pre-cargar relación 'certificates'
        .where(UserModel.user_id == user_id)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # Si no existe el usuario, lanza un 404
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Retorna el usuario encontrado
    return UserSchema.model_validate(user)