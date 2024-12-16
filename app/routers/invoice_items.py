from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud, schemas

router = APIRouter()

@router.post("/invoice-items/", response_model=schemas.InvoiceItem)
async def create_invoice_item(invoice_item: schemas.InvoiceItemCreate, db: AsyncSession = Depends(get_db)):
    db_invoice_item = await crud.create_invoice_item(db, invoice_item)
    return schemas.InvoiceItem.model_validate(db_invoice_item)

@router.get("/invoice-items/{item_id}", response_model=schemas.InvoiceItem)
async def read_invoice_item(item_id: int, db: AsyncSession = Depends(get_db)):
    db_invoice_item = await crud.get_invoice_item(db, item_id)
    if not db_invoice_item:
        raise HTTPException(status_code=404, detail="Invoice item not found")
    return schemas.InvoiceItem.model_validate(db_invoice_item)