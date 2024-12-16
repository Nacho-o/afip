from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import Authorization as AuthorizationModel, Certificate as CertificateModel
from app.schemas import Authorization as AuthorizationSchema
from app.database import get_db
from typing import List
from afip import Afip
import asyncio
import logging
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class AuthorizationRequest(BaseModel):
    user_id: int
    service: str

@router.post("/authorizations/", response_model=AuthorizationSchema)
async def create_authorization(request: AuthorizationRequest, db: AsyncSession = Depends(get_db)):
    user_id = request.user_id
    service = request.service

    # Buscar el certificado más reciente del usuario
    stmt = (
        select(CertificateModel)
        .where(CertificateModel.user_id == user_id)
        .options(selectinload(CertificateModel.user))  # Pre-cargar relación 'user'
        .order_by(CertificateModel.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    db_certificate = result.scalar_one_or_none()

    if not db_certificate:
        raise HTTPException(status_code=404, detail="No certificate found for this user")
    
    # Verificar si el certificado ha expirado
    if db_certificate.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Certificate has expired")

    # Verificar si ya existe una autorización para este servicio y certificado
    stmt = (
        select(AuthorizationModel)
        .where(
            AuthorizationModel.certificate_id == db_certificate.certificate_id,
            AuthorizationModel.service == service
        )
    )
    result = await db.execute(stmt)
    existing_auth = result.scalar_one_or_none()

    if existing_auth:
        logging.info(f"La autorización para el servicio '{service}' ya existe en la base de datos.")
        return AuthorizationSchema.model_validate(existing_auth)

    afip = Afip({"CUIT": db_certificate.user.cuit})
    max_retries = 3
    retry_interval = 3

    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"Intento {attempt} de autorizar el servicio '{service}'...")
            auth_response = afip.createWSAuth(
                db_certificate.user.username, 
                db_certificate.user.password_hash, 
                db_certificate.cert_alias, 
                service
            )
            
            status = auth_response.get("status", "").strip().lower()
            logging.info(f"Respuesta de AFIP: {auth_response}")
            
            # Si el estado es "created", guardar en la base de datos y detener el bucle
            if status == "created":
                logging.info(f"Autorización completada con estado: {status}")
                db_auth = AuthorizationModel(
                    certificate_id=db_certificate.certificate_id,
                    service=service,
                    status=status,
                )
                db.add(db_auth)
                await db.commit()
                await db.refresh(db_auth)
                return AuthorizationSchema.model_validate(db_auth)

            # Si el estado es "exists", devolver el registro existente
            elif status == "exists":
                logging.info(f"El servicio '{service}' ya está autorizado en AFIP con estado '{status}'.")
                return AuthorizationSchema(
                    authorization_id=None,  # No agregar un nuevo ID porque no se guarda en la base de datos
                    certificate_id=db_certificate.certificate_id,
                    service=service,
                    status=status,
                    created_at=None,  # Opcional: Puedes devolver valores nulos aquí si no hay un registro en la base de datos
                    updated_at=None,
                )

        except Exception as e:
            logging.error(f"Error al autorizar servicio '{service}' en intento {attempt}: {e}")

        # Si no es el último intento, esperar antes de reintentar
        if attempt < max_retries:
            logging.info(f"Esperando {retry_interval} segundos antes de reintentar...")
            await asyncio.sleep(retry_interval)

    # Si se alcanzó el número máximo de intentos sin éxito
    raise HTTPException(status_code=500, detail="No se pudo completar la autorización después de múltiples intentos.")

@router.get("/authorizations/{user_id}", response_model=List[AuthorizationSchema])
async def get_user_authorizations(user_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(AuthorizationModel)
        .options(selectinload(AuthorizationModel.certificate))  # Pre-cargar relación 'certificate'
        .where(AuthorizationModel.certificate.has(user_id=user_id))  # Relación entre tablas
    )
    result = await db.execute(stmt)
    authorizations = result.scalars().all()
    if not authorizations:
        raise HTTPException(status_code=404, detail="No authorizations found for this user")
    return [AuthorizationSchema.model_validate(auth) for auth in authorizations]

@router.get("/authorizations/by_certificate/{certificate_id}", response_model=List[AuthorizationSchema])
async def get_authorizations_by_certificate(certificate_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(AuthorizationModel)
        .where(AuthorizationModel.certificate_id == certificate_id)
    )
    result = await db.execute(stmt)
    authorizations = result.scalars().all()
    if not authorizations:
        raise HTTPException(status_code=404, detail="No authorizations found for this certificate")
    return [AuthorizationSchema.model_validate(auth) for auth in authorizations]