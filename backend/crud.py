from sqlalchemy.orm import Session
import models, schemas, security

def get_user_by_username(db: Session, username: str):
    """Busca un usuario por su nombre de usuario."""
    return db.query(models.User).filter(models.User.username == username).first()

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