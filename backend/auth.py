from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt

import crud, models, schemas, security
from database import SessionLocal

router = APIRouter(prefix="/auth", tags=["Autenticación"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/users/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Endpoint para registrar un nuevo usuario."""
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    return crud.create_user(db=db, user=user)

@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Endpoint para iniciar sesión y obtener un token."""
    print("--- LOGIN ATTEMPT ---")
    print(f"Attempting login for username: '{form_data.username}'")

    user = crud.get_user_by_username(db, username=form_data.username)

    if not user:
        print("DEBUG: User not found in database.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"DEBUG: User '{user.username}' found in database.")
    print(f"DEBUG: Hashed password from DB: {user.hashed_password}")
    
    is_password_correct = security.verify_password(form_data.password, user.hashed_password)
    
    print(f"DEBUG: Password verification result: {is_password_correct}")

    if not is_password_correct:
        print("DEBUG: Password verification FAILED.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print("DEBUG: Password verification SUCCEEDED.")
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(security.oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

@router.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Devuelve los datos del usuario actualmente logueado."""
    return current_user

async def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    """
    Dependencia que verifica si el usuario actual es un administrador.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes los permisos necesarios para esta operación."
        )
    return current_user