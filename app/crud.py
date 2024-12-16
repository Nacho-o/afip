from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from . import models, schemas
from sqlalchemy.orm import joinedload
from app.models import Certificate, Authorization
from app.schemas import CertificateCreate, AuthorizationCreate
import logging

# Users CRUD operations
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).filter(models.User.user_id == user_id))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    logging.debug(f"Creando usuario en la base de datos: {user.model_dump()}")
    try:
        db_user = models.User(
            username=user.username,
            password_hash=user.password_hash,
            email=user.email,
            cuit=user.cuit,
            full_name=user.full_name,
            is_active=True
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        logging.debug(f"Usuario creado: {db_user}")
        return db_user
    except Exception as e:
        logging.error(f"Error al crear usuario: {e}")
        raise

async def update_user(db: AsyncSession, user_id: int, user_update: schemas.UserUpdate):
    result = await db.execute(select(models.User).filter(models.User.user_id == user_id))
    db_user = result.scalars().first()
    if db_user:
        for key, value in user_update.model_dump(exclude_unset=True).items():
            setattr(db_user, key, value)
        await db.commit()
        await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).filter(models.User.user_id == user_id))
    db_user = result.scalars().first()
    if db_user:
        await db.delete(db_user)
        await db.commit()
    return db_user

# Clients CRUD operations
async def get_client(db: AsyncSession, client_id: int):
    result = await db.execute(select(models.Client).filter(models.Client.client_id == client_id))
    return result.scalars().first()

async def create_client(db: AsyncSession, client: schemas.ClientCreate):
    db_client = models.Client(
        user_id=client.user_id,
        name=client.name,
        cuit=client.cuit,
        tax_condition=client.tax_condition,
        email=client.email,
        phone=client.phone,
        address=client.address,
        is_active=True
    )
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
    return db_client

async def update_client(db: AsyncSession, client_id: int, client_update: schemas.ClientUpdate):
    result = await db.execute(select(models.Client).filter(models.Client.client_id == client_id))
    db_client = result.scalars().first()
    if db_client:
        for key, value in client_update.model_dump(exclude_unset=True).items():
            setattr(db_client, key, value)
        await db.commit()
        await db.refresh(db_client)
    return db_client

async def delete_client(db: AsyncSession, client_id: int):
    result = await db.execute(select(models.Client).filter(models.Client.client_id == client_id))
    db_client = result.scalars().first()
    if db_client:
        await db.delete(db_client)
        await db.commit()
    return db_client

# Invoices CRUD operations
async def get_invoice(db: AsyncSession, invoice_id: int):
    result = await db.execute(select(models.Invoice).filter(models.Invoice.invoice_id == invoice_id))
    return result.scalars().first()

async def create_invoice(db: AsyncSession, invoice: schemas.InvoiceCreate):
    db_invoice = models.Invoice(
        user_id=invoice.user_id,
        client_id=invoice.client_id,
        invoice_number=invoice.invoice_number,
        invoice_type=invoice.invoice_type,
        point_of_sale=invoice.point_of_sale,
        date=invoice.date,
        total_amount=invoice.total_amount,
        net_amount=invoice.net_amount,
        tax_amount=invoice.tax_amount,
        cae=invoice.cae,
        cae_expiration_date=invoice.cae_expiration_date,
        status=invoice.status
    )
    db.add(db_invoice)
    await db.commit()
    await db.refresh(db_invoice)
    return db_invoice

async def update_invoice(db: AsyncSession, invoice_id: int, invoice_update: schemas.InvoiceUpdate):
    result = await db.execute(select(models.Invoice).filter(models.Invoice.invoice_id == invoice_id))
    db_invoice = result.scalars().first()
    if db_invoice:
        for key, value in invoice_update.model_dump(exclude_unset=True).items():
            setattr(db_invoice, key, value)
        await db.commit()
        await db.refresh(db_invoice)
    return db_invoice

async def delete_invoice(db: AsyncSession, invoice_id: int):
    result = await db.execute(select(models.Invoice).filter(models.Invoice.invoice_id == invoice_id))
    db_invoice = result.scalars().first()
    if db_invoice:
        await db.delete(db_invoice)
        await db.commit()
    return db_invoice

# Invoice Items CRUD operations
async def get_invoice_item(db: AsyncSession, item_id: int):
    result = await db.execute(select(models.InvoiceItem).filter(models.InvoiceItem.item_id == item_id))
    return result.scalars().first()

async def create_invoice_item(db: AsyncSession, invoice_item: schemas.InvoiceItemCreate):
    db_item = models.InvoiceItem(
        invoice_id=invoice_item.invoice_id,
        description=invoice_item.description,
        quantity=invoice_item.quantity,
        unit_price=invoice_item.unit_price,
        total_price=invoice_item.total_price,
        tax_rate=invoice_item.tax_rate,
        tax_amount=invoice_item.tax_amount
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def update_invoice_item(db: AsyncSession, item_id: int, item_update: schemas.InvoiceItemUpdate):
    result = await db.execute(select(models.InvoiceItem).filter(models.InvoiceItem.item_id == item_id))
    db_item = result.scalars().first()
    if db_item:
        for key, value in item_update.model_dump(exclude_unset=True).items():
            setattr(db_item, key, value)
        await db.commit()
        await db.refresh(db_item)
    return db_item

async def delete_invoice_item(db: AsyncSession, item_id: int):
    result = await db.execute(select(models.InvoiceItem).filter(models.InvoiceItem.item_id == item_id))
    db_item = result.scalars().first()
    if db_item:
        await db.delete(db_item)
        await db.commit()
    return db_item

# Certificates CRUD operations
async def get_certificate(db: AsyncSession, certificate_id: int):
    result = await db.execute(select(models.Certificate).filter(models.Certificate.certificate_id == certificate_id))
    return result.scalars().first()

async def create_certificate(db: AsyncSession, certificate: CertificateCreate, user_id: int):
    db_certificate = Certificate(
        cert_alias=certificate.cert_alias,
        certificate=certificate.certificate,
        private_key=certificate.private_key,
        user_id=user_id
    )
    db.add(db_certificate)
    await db.commit()
    await db.refresh(db_certificate)
    return db_certificate

async def update_certificate(db: AsyncSession, certificate_id: int, cert_update: schemas.CertificateUpdate):
    result = await db.execute(select(models.Certificate).filter(models.Certificate.certificate_id == certificate_id))
    db_certificate = result.scalars().first()
    if db_certificate:
        for key, value in cert_update.model_dump(exclude_unset=True).items():
            setattr(db_certificate, key, value)
        await db.commit()
        await db.refresh(db_certificate)
    return db_certificate

async def delete_certificate(db: AsyncSession, certificate_id: int):
    result = await db.execute(select(models.Certificate).filter(models.Certificate.certificate_id == certificate_id))
    db_certificate = result.scalars().first()
    if db_certificate:
        await db.delete(db_certificate)
        await db.commit()
    return db_certificate

async def create_authorization(db: AsyncSession, user_id: int, service: str):
    db_auth = Authorization(user_id=user_id, service=service, status="pending")
    db.add(db_auth)
    await db.commit()
    await db.refresh(db_auth)
    return db_auth

async def update_authorization_status(db: AsyncSession, authorization_id: int, status: str):
    stmt = select(Authorization).where(Authorization.authorization_id == authorization_id)
    result = await db.execute(stmt)
    db_auth = result.scalar_one_or_none()
    if db_auth:
        db_auth.status = status
        await db.commit()
        await db.refresh(db_auth)
    return db_auth