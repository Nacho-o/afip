from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud, schemas

router = APIRouter()

@router.post("/clients/", response_model=schemas.Client)
async def create_client(client: schemas.ClientCreate, db: AsyncSession = Depends(get_db)):
    db_client = await crud.create_client(db, client)
    return schemas.Client.model_validate(db_client)

@router.get("/clients/{client_id}", response_model=schemas.Client)
async def read_client(client_id: int, db: AsyncSession = Depends(get_db)):
    db_client = await crud.get_client(db, client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return schemas.Client.model_validate(db_client)