# backend/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

import models, auth, schemas
from database import SessionLocal

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/stats", dependencies=[Depends(auth.get_current_user)])
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Calcula y devuelve las estadísticas principales para la barra de resumen.
    """
    # Cuenta cuántos trabajos hay en cada estado (excluyendo 'entregado al cliente')
    counts_por_estado = (
        db.query(models.Trabajo.estado_actual, func.count(models.Trabajo.id))
        .filter(models.Trabajo.estado_actual != "entregado al cliente")
        .group_by(models.Trabajo.estado_actual)
        .all()
    )

    # Puedes añadir más métricas aquí, como alertas, etc.

    return {"counts_por_estado": dict(counts_por_estado)}