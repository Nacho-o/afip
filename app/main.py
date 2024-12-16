from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers import users, clients, invoices, certificates, invoice_items, authorizations
from app.database import engine
from pydantic_settings import BaseSettings
import logging
import traceback

class Settings(BaseSettings):
    database_url: str

    class ConfigDict:
        env_file = ".env"

settings = Settings()

# Configuración principal de la aplicación
app = FastAPI()

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Middleware para capturar errores y mostrar más detalles
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # Capturar el error completo
        error_trace = traceback.format_exc()
        logger.error(f"Unhandled error: {e}")
        logger.error(f"Traceback: {error_trace}")
        
        # Retornar un JSON con detalles del error
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "error": str(e), "trace": error_trace},
        )

# Registrar los routers (endpoints)
app.include_router(users.router, prefix="/api/v1")
app.include_router(clients.router, prefix="/api/v1")
app.include_router(invoices.router, prefix="/api/v1")
app.include_router(certificates.router, prefix="/api/v1")
app.include_router(invoice_items.router, prefix="/api/v1")
app.include_router(authorizations.router, prefix="/api/v1")