# backend/create_admin.py
from sqlalchemy.orm import Session
import crud, schemas
from database import SessionLocal

def create_super_user():
    db: Session = SessionLocal()

    print("--- Creando Super Administrador ---")

    # Pide los datos por terminal
    username = input("Ingresa el nombre de usuario del admin: ")
    email = input("Ingresa el email del admin: ")
    password = input("Ingresa la contraseña del admin: ")

    user_in = schemas.UserCreate(username=username, email=email, password=password)

    # Revisa si el usuario ya existe
    db_user = crud.get_user_by_username(db, username=user_in.username)
    if db_user:
        print(f"El usuario '{db_user.username}' ya existe. Quieres actualizar su rol a 'admin'? (s/n)")
        choice = input().lower()
        if choice == 's':
            db_user.role = "admin"
            db.commit()
            print("Rol de usuario actualizado a 'admin'.")
        else:
            print("Operación cancelada.")
    else:
        # Crea el nuevo usuario
        new_user = crud.create_user(db, user=user_in)
        # Le asigna el rol de admin
        new_user.role = "admin"
        db.commit()
        print(f"Usuario admin '{new_user.username}' creado exitosamente.")

    db.close()

if __name__ == "__main__":
    create_super_user()