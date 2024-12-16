from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from decouple import config
import asyncio
from sqlalchemy import text

# Leer la URL de conexión desde el archivo .env
DATABASE_URL = config("DATABASE_URL", default=None)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Please define it in your .env file.")

# Crear el motor de conexión
engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
async_session = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Declarative base para los modelos
Base = declarative_base()

# Verificar conexión a la base de datos
async def test_connection():
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
            print("Database connected successfully!")
    except Exception as e:
        print(f"Database connection failed: {e}")

# Dependency para obtener una sesión asincrónica de la base de datos
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# Si ejecutas el archivo directamente, prueba la conexión
if __name__ == "__main__":
    asyncio.run(test_connection())