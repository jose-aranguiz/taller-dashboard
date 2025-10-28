from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional # <-- IMPORTACIÓN AÑADIDA
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv

load_dotenv() # Carga las variables de entorno desde un archivo .env

# --- CONFIGURACIÓN DE SEGURIDAD ---

# 1. Clave secreta para firmar los tokens. ¡DEBE SER SECRETA!
#    Genera una con: openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY", "una-clave-secreta-muy-larga-y-dificil-de-adivinar")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Tiempo de vida del token

# 2. Contexto de Passlib para el hasheo de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 3. Esquema OAuth2 para que FastAPI sepa cómo esperar el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# --- FUNCIONES DE UTILIDAD ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con una hasheada."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña."""
    return pwd_context.hash(password)

# ↓↓↓ CAMBIO REALIZADO AQUÍ ↓↓↓
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un nuevo token de acceso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Si no se especifica un delta, el token dura lo que diga la constante de configuración
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt