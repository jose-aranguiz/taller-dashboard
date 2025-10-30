from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud, models, schemas, auth 
from database import get_db 

router = APIRouter(prefix="/tecnicos", tags=["Técnicos"])

# --- Endpoints ---

@router.get("/", response_model=List[schemas.Tecnico])
def get_all_tecnicos(
    db: Session = Depends(get_db),
    # 👇 Añadimos autenticación a esta ruta también
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Obtiene todos los técnicos."""
    return crud.get_tecnicos(db)

@router.post("/", response_model=schemas.Tecnico, status_code=status.HTTP_201_CREATED)
def create_new_tecnico(
    tecnico: schemas.TecnicoCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_admin_user) 
):
    """Crea un nuevo técnico (requiere ser admin)."""
    # Verificamos si ya existe
    db_tecnico = db.query(models.Tecnico).filter(models.Tecnico.nombre == tecnico.nombre).first()
    if db_tecnico:
        raise HTTPException(status_code=400, detail="Ya existe un técnico con este nombre")
    return crud.create_tecnico(db=db, tecnico=tecnico)

@router.delete("/{tecnico_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_tecnico(
    tecnico_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    """Elimina un técnico por ID (requiere ser admin)."""
    db_tecnico = crud.get_tecnico(db, tecnico_id=tecnico_id)
    if db_tecnico is None:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    
    # --- 👇 ESTA LÍNEA AHORA FUNCIONARÁ ---
    # (Gracias a los cambios en models.py)
    if db_tecnico.trabajos_asignados: 
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No se puede eliminar un técnico que está asignado a trabajos."
        )

    crud.delete_tecnico(db=db, tecnico_id=tecnico_id)
    return None # No Content