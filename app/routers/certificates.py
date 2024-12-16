from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from app.database import get_db
from app.models import Certificate as CertificateModel, User as UserModel
from app.schemas import Certificate as CertificateSchema
from afip import Afip
from pydantic import BaseModel

router = APIRouter()

class CertificateRequest(BaseModel):
    user_id: int

@router.post("/certificates/", response_model=CertificateSchema)
async def create_certificate(request: CertificateRequest, db: AsyncSession = Depends(get_db)):
    user_id = request.user_id

    # Verificar si el usuario existe
    stmt = (
        select(UserModel)
        .where(UserModel.user_id == user_id)
        .options(selectinload(UserModel.certificates))  # Pre-cargar relación 'certificates'
    )
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verificar si ya existe un certificado para el usuario
    if db_user.certificates:
        return CertificateSchema.model_validate(db_user.certificates[0])

    # Crear el certificado
    afip = Afip({"CUIT": db_user.cuit})
    try:
        response = afip.createCert(db_user.username, db_user.password_hash, "afipsdk")
        cert = response.get("cert")
        key = response.get("key")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear certificado en AFIP: {e}")

    db_certificate = CertificateModel(
        user_id=user_id,
        cert_alias="afipsdk",
        certificate=cert,
        private_key=key,
    )
    db.add(db_certificate)
    await db.commit()
    await db.refresh(db_certificate)

    return CertificateSchema.model_validate(db_certificate)

@router.get("/certificates/{certificate_id}", response_model=CertificateSchema)
async def read_certificate(certificate_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(CertificateModel)
        .where(CertificateModel.certificate_id == certificate_id)
        .options(selectinload(CertificateModel.user))  # Pre-cargar relación 'user'
    )
    result = await db.execute(stmt)
    db_certificate = result.scalar_one_or_none()

    if not db_certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")

    return CertificateSchema.model_validate(db_certificate)

@router.get("/certificates/by_user/{user_id}", response_model=List[CertificateSchema])
async def get_certificates_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(CertificateModel)
        .where(CertificateModel.user_id == user_id)
        .options(selectinload(CertificateModel.user))  # Pre-cargar relación 'user'
    )
    result = await db.execute(stmt)
    certificates = result.scalars().all()

    if not certificates:
        raise HTTPException(status_code=404, detail="No certificates found for this user")

    return [CertificateSchema.model_validate(cert) for cert in certificates]