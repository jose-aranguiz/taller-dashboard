# backend/tests/conftest.py
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from alembic.config import Config
from alembic import command

# --- IMPORTANTE: Estas son las importaciones correctas ---
from main import app 
from database import Base, get_db
import crud, schemas, models
from security import get_password_hash
# -----------------------------------------------------

# --- CONFIGURACIÓN DE BBDD DE PRUEBA ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
os.environ["DATABASE_URL"] = SQLALCHEMY_DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- CREACIÓN Y DESTRUCCIÓN DE LA BBDD DE PRUEBA ---

@pytest.fixture(scope="session")
def db_engine():
    """
    Fixture de Pytest: Crea la base de datos y las tablas una vez por sesión.
    """
    if os.path.exists("./test.db"):
        os.remove("./test.db")
        
    print("Creando base de datos de prueba...")
    Base.metadata.create_all(bind=engine)
    yield engine
    print("\nCerrando engine y borrando base de datos de prueba...")
    engine.dispose()
    os.remove("./test.db")


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Fixture de Pytest: Crea una sesión de BBDD limpia para CADA prueba.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


# --- CLIENTE DE PRUEBA DE FASTAPI ---

@pytest.fixture(scope="function")
def client(db_session):
    """
    Fixture de Pytest: Crea un cliente de API para CADA prueba.
    """
    
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client

# --- FIXTURES DE AUTENTICACIÓN ---

@pytest.fixture(scope="function")
def test_user_admin(db_session: Session):
    """
    Crea un usuario administrador de prueba en la BBDD.
    """
    user_in = schemas.UserCreate(
        username="testadmin",
        email="admin@test.com",
        password="testpassword"
    )
    user = crud.create_user(db=db_session, user=user_in)
    user.role = "admin" # Lo hacemos admin
    db_session.commit()
    return user

@pytest.fixture(scope="function")
def admin_token_headers(client: TestClient, test_user_admin: models.User) -> dict[str, str]:
    """
    Inicia sesión como el usuario admin de prueba y devuelve las cabeceras de autorización.
    """
    login_data = {
        "username": test_user_admin.username,
        "password": "testpassword" # La contraseña en texto plano
    }
    response = client.post("/token", data=login_data)
    
    assert response.status_code == 200, "No se pudo iniciar sesión para la prueba"
    
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    return headers