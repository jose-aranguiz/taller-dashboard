from sqlalchemy.orm import Session
import models, schemas, security

# --- Funciones CRUD para Usuarios (Tu código original) ---

def get_user_by_username(db: Session, username: str):
    """Busca un usuario por su nombre de usuario."""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """Busca un usuario por su email (necesario para auth.py)."""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Crea un nuevo usuario en la base de datos."""
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Funciones CRUD para Tecnicos (Añadidas para corregir errores) ---

def get_tecnico(db: Session, tecnico_id: int):
    """Obtiene un técnico por su ID."""
    return db.query(models.Tecnico).filter(models.Tecnico.id == tecnico_id).first()

def get_tecnicos(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene una lista de técnicos (esta era la que faltaba)."""
    return db.query(models.Tecnico).offset(skip).limit(limit).all()

def create_tecnico(db: Session, tecnico: schemas.TecnicoCreate):
    """Crea un nuevo técnico."""
    db_tecnico = models.Tecnico(nombre=tecnico.nombre)
    db.add(db_tecnico)
    db.commit()
    db.refresh(db_tecnico)
    return db_tecnico

def delete_tecnico(db: Session, tecnico_id: int):
    """Elimina un técnico por ID."""
    db_tecnico = db.query(models.Tecnico).filter(models.Tecnico.id == tecnico_id).first()
    if db_tecnico:
        db.delete(db_tecnico)
        db.commit()
    return db_tecnico

# --- Añade aquí más funciones CRUD para Trabajos si las necesitas ---