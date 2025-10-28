# backend/celery_worker.py

import os
from celery import Celery
from celery.schedules import crontab
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models

# --- CONFIGURACIÓN ---
# Usamos variables de entorno como en docker-compose
celery_broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
celery_result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
database_url = os.environ.get("DATABASE_URL", "postgresql://admin:admin@taller_db:5432/taller_db")

# --- INSTANCIA DE CELERY ---
celery_app = Celery(
    __name__,
    broker=celery_broker_url,
    backend=celery_result_backend
)

# --- CONEXIÓN A LA BASE DE DATOS (independiente de FastAPI) ---
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --- TAREA PROGRAMADA ---
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Ejecuta la tarea cada 10 minutos
    sender.add_periodic_task(
        crontab(minute='*/10'),
        revisar_vehiculos_en_espera.s(),
        name='revisar vehiculos en espera cada 10 mins'
    )

@celery_app.task
def revisar_vehiculos_en_espera():
    """
    Busca vehículos en estados que requieren monitoreo y verifica su tiempo de permanencia.
    """
    print(f"--- Ejecutando revisión de vehículos a las {datetime.datetime.now()} ---")
    db = SessionLocal()
    try:
        # Estados que queremos monitorear y sus límites de tiempo en horas
        ESTADOS_A_MONITOREAR = {
            "espera de trabajo": 2,
            "trabajo detenido": 24
        }
        
        ahora = datetime.datetime.utcnow()

        for estado, limite_horas in ESTADOS_A_MONITOREAR.items():
            # Buscamos el último historial sin fecha_fin para los trabajos en el estado actual
            subquery = db.query(
                models.HistorialDeEstado.trabajo_id,
                func.max(models.HistorialDeEstado.fecha_inicio).label('max_fecha_inicio')
            ).filter(
                models.HistorialDeEstado.estado == estado,
                models.HistorialDeEstado.fecha_fin == None
            ).group_by(models.HistorialDeEstado.trabajo_id).subquery()

            trabajos_a_revisar = db.query(models.Trabajo).join(
                subquery, models.Trabajo.id == subquery.c.trabajo_id
            ).all()

            print(f"Encontrados {len(trabajos_a_revisar)} trabajos en '{estado}' para revisar.")

            for trabajo in trabajos_a_revisar:
                # El historial actual es el que no tiene fecha_fin
                historial_actual = next((h for h in trabajo.historial if h.fecha_fin is None), None)
                if not historial_actual: continue

                tiempo_en_estado = ahora - historial_actual.fecha_inicio
                if tiempo_en_estado > datetime.timedelta(hours=limite_horas):
                    print(f"[ALERTA!] El trabajo {trabajo.patente} (ID: {trabajo.id}) ha superado las {limite_horas} horas en estado '{estado}'.")
                    # Aquí es donde, en el futuro, enviaremos la notificación por WebSocket
    finally:
        db.close()
    
    return "Revisión completada."