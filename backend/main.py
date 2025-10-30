from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine # Importamos engine
# 👇 IMPORTANTE: Importamos models pero NO lo usamos aquí directamente
import models 
from auth import router as auth_router
from trabajos import router as trabajos_router
from tecnicos import router as tecnicos_router
from dashboard import router as dashboard_router

# --- 🛑 LÍNEA ELIMINADA O COMENTADA 🛑 ---
# models.Base.metadata.create_all(bind=engine) 
# La creación de tablas se maneja externamente (ej. con Alembic o en tests)
# ------------------------------------------

app = FastAPI(title="API Taller Dashboard", version="0.1.0")

# Configuración de CORS
origins = [
    "http://localhost:9000",  # URL de desarrollo de Quasar
    "http://localhost:8080",  # Otra posible URL de desarrollo
    # Puedes añadir aquí la URL de producción cuando la tengas
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers
app.include_router(auth_router)
app.include_router(trabajos_router)
app.include_router(tecnicos_router)
app.include_router(dashboard_router)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bienvenido a la API del Taller Dashboard"}

# Aquí podrías añadir eventos de startup/shutdown si los necesitas en el futuro
# @app.on_event("startup")
# async def startup_event():
#     # Código a ejecutar al iniciar la app (si es necesario)
#     pass

# @app.on_event("shutdown")
# async def shutdown_event():
#     # Código a ejecutar al detener la app (si es necesario)
#     pass