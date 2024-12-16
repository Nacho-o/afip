from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud, schemas

router = APIRouter()

@router.post("/invoices/", response_model=schemas.Invoice)
async def create_invoice(invoice: schemas.InvoiceCreate, db: AsyncSession = Depends(get_db)):
    db_invoice = await crud.create_invoice(db, invoice)
    return schemas.Invoice.model_validate(db_invoice)

@router.get("/invoices/{invoice_id}", response_model=schemas.Invoice)
async def read_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    db_invoice = await crud.get_invoice(db, invoice_id)
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return schemas.Invoice.model_validate(db_invoice)