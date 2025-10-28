# backend/tecnicos.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models, auth, schemas
from database import SessionLocal

router = APIRouter(prefix="/tecnicos", tags=["Técnicos"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.Tecnico], dependencies=[Depends(auth.get_current_user)])
def get_all_tecnicos(db: Session = Depends(get_db)):
    """Devuelve una lista de todos los técnicos."""
    return db.query(models.Tecnico).all()

@router.post("/", response_model=schemas.Tecnico, dependencies=[Depends(auth.get_current_admin_user)])
def create_tecnico(tecnico: schemas.TecnicoCreate, db: Session = Depends(get_db)):
    """Crea un nuevo técnico (solo para admins)."""
    db_tecnico = db.query(models.Tecnico).filter(models.Tecnico.codigo == tecnico.codigo).first()
    if db_tecnico:
        raise HTTPException(status_code=400, detail="El código de técnico ya existe.")
    new_tecnico = models.Tecnico(**tecnico.model_dump())
    db.add(new_tecnico)
    db.commit()
    db.refresh(new_tecnico)
    return new_tecnico