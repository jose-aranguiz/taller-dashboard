from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional 
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
# 👇 Importaciones necesarias para authenticate_user
from sqlalchemy.orm import Session
import crud # Necesitamos crud para buscar al usuario
import models # Necesitamos models para el tipado

load_dotenv() 

# --- CONFIGURACIÓN DE SEGURIDAD ---

SECRET_KEY = os.getenv("SECRET_KEY", "una-clave-secreta-muy-larga-y-dificil-de-adivinar")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 👇 CORRECCIÓN: Apunta a /token, la ruta definida en auth.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token") 


# --- FUNCIONES DE UTILIDAD ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con una hasheada."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un nuevo token de acceso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- 👇 NUEVA FUNCIÓN: Lógica de Autenticación ---
def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """
    Busca un usuario por username y verifica su contraseña.
    Devuelve el objeto User si es válido, None si no.
    """
    user = crud.get_user_by_username(db, username=username)
    if not user:
        return None # Usuario no encontrado
    if not verify_password(password, user.hashed_password):
        return None # Contraseña incorrecta
    return user # Usuario y contraseña válidos