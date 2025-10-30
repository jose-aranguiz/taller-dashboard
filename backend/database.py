from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session # <-- Importamos Session
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db/tallerdb")

engine = create_engine(DATABASE_URL)

if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- 👇 FUNCIÓN get_db AÑADIDA AQUÍ (Paso 8 - Corrección) ---
def get_db():
    """
    Función de dependencia de FastAPI para obtener una sesión de base de datos.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# --- FIN DE LA FUNCIÓN AÑADIDA ---