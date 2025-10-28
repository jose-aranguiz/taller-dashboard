from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Body, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, inspect
from typing import List, Optional
import models, schemas, auth
from database import SessionLocal
import datetime
import pandas as pd
import io
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VALID_TRANSITIONS = {
    "agendado": ["espera de trabajo"], "espera de trabajo": ["en trabajo", "en lavado"],
    "en trabajo": ["trabajo detenido", "control de calidad", "en lavado"], "trabajo detenido": ["en trabajo"],
    "en lavado": ["espera de trabajo", "en trabajo", "control de calidad"], "control de calidad": ["listo para entrega", "en trabajo"],
    "listo para entrega": ["entregado al cliente"], "entregado al cliente": []
}

router = APIRouter(prefix="/trabajos", tags=["Trabajos"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=schemas.PaginatedTrabajos)
def leer_trabajos_paginados(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 15,
    sort_by: Optional[str] = "id",
    sort_order: str = "desc",
    search: Optional[str] = None,
    asesor_servicio: Optional[str] = None,
    estado_actual: Optional[str] = Query(None),
    fecha_desde: Optional[datetime.date] = Query(None),
    fecha_hasta: Optional[datetime.date] = Query(None),
    # --- ✨ NUEVOS PARÁMETROS PARA HISTORIAL ---
    activos: bool = True,
    patente: Optional[str] = None,
    # ----------------------------------------
    current_user: schemas.User = Depends(auth.get_current_user)
):
    try:
        query = db.query(models.Trabajo)

        # --- ✨ LÓGICA DE FILTRADO MODIFICADA ---
        if patente:
            # Si se busca una patente, se obtiene todo su historial sin paginación.
            query = query.filter(models.Trabajo.patente.ilike(f"%{patente}%")).order_by(models.Trabajo.fecha_creacion_pedido.desc())
        else:
            # Lógica para la vista principal (activos) y la página de historial (inactivos)
            if activos:
                query = query.filter(models.Trabajo.estado_actual != 'entregado al cliente')
            else:
                query = query.filter(models.Trabajo.estado_actual == 'entregado al cliente')

            if search:
                query = query.filter(or_(
                    models.Trabajo.cliente_nombre.ilike(f"%{search}%"),
                    models.Trabajo.patente.ilike(f"%{search}%"),
                    models.Trabajo.pedido_dbm.ilike(f"%{search}%")
                ))
            
            if asesor_servicio:
                query = query.filter(models.Trabajo.asesor_servicio.ilike(f"%{asesor_servicio}%"))
            if estado_actual:
                query = query.filter(models.Trabajo.estado_actual == estado_actual)
            if fecha_desde:
                query = query.filter(models.Trabajo.fecha_creacion_pedido >= fecha_desde)
            if fecha_hasta:
                query = query.filter(models.Trabajo.fecha_creacion_pedido < fecha_hasta + datetime.timedelta(days=1))
        # ------------------------------------

        total_records = query.count()

        if sort_by and hasattr(models.Trabajo, sort_by):
            columna_a_ordenar = getattr(models.Trabajo, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(columna_a_ordenar.desc())
            else:
                query = query.order_by(columna_a_ordenar.asc())
        
        offset = (page - 1) * limit
        items = query.offset(offset).limit(limit).all()
        
        # --- Cálculo de días de estadía (se mantiene igual) ---
        for trabajo in items:
            try:
                fecha_inicio_conteo = trabajo.fecha_llegada_taller or trabajo.fecha_creacion_pedido
                if not fecha_inicio_conteo:
                    trabajo.dias_de_estadia_activa = 0
                    continue

                if hasattr(fecha_inicio_conteo, 'tzinfo') and fecha_inicio_conteo.tzinfo is not None:
                    fecha_inicio_conteo = fecha_inicio_conteo.replace(tzinfo=None)

                tiempo_total_segundos = (datetime.datetime.utcnow() - fecha_inicio_conteo).total_seconds()
                
                tiempo_detenido_segundos = db.query(
                    func.sum(func.extract('epoch', func.coalesce(models.HistorialDeEstado.fecha_fin, func.now()) - models.HistorialDeEstado.fecha_inicio))
                ).filter(
                    models.HistorialDeEstado.trabajo_id == trabajo.id,
                    models.HistorialDeEstado.estado == 'trabajo detenido'
                ).scalar() or 0
                tiempo_activo_segundos = tiempo_total_segundos - tiempo_detenido_segundos
                trabajo.dias_de_estadia_activa = int(tiempo_activo_segundos / (24 * 3600)) if tiempo_activo_segundos > 0 else 0
            except Exception as e:
                logger.error(f"Error calculando días de estadía para trabajo ID {trabajo.id}: {e}")
                trabajo.dias_de_estadia_activa = -1

        return {"items": items, "total": total_records}

    except Exception as e:
        logger.error(f"Error fatal en leer_trabajos_paginados: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ocurrió un error inesperado en el servidor al listar los trabajos.")

# --- EL RESTO DE LAS RUTAS SE MANTIENEN IGUAL ---

@router.patch("/{trabajo_id}", response_model=schemas.Trabajo)
def actualizar_trabajo(
    trabajo_id: int, 
    trabajo_update: schemas.TrabajoUpdate, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    trabajo_db = db.query(models.Trabajo).filter(models.Trabajo.id == trabajo_id).first()
    if not trabajo_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    update_data = trabajo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(trabajo_db, key, value)
    
    db.commit()
    db.refresh(trabajo_db)
    return trabajo_db

@router.patch("/{trabajo_id}/estado", response_model=schemas.Trabajo)
def actualizar_estado_trabajo(
    trabajo_id: int, 
    estado_update: schemas.TrabajoUpdateEstado = Body(...), 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    trabajo_db = db.query(models.Trabajo).filter(models.Trabajo.id == trabajo_id).first()
    if not trabajo_db: raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    estado_actual = trabajo_db.estado_actual
    nuevo_estado = estado_update.nuevo_estado

    if estado_actual in VALID_TRANSITIONS and nuevo_estado not in VALID_TRANSITIONS[estado_actual]:
        raise HTTPException(status_code=400, detail=f"Transición no permitida de '{estado_actual}' a '{nuevo_estado}'")
    if nuevo_estado == "trabajo detenido" and not estado_update.motivo_detencion:
        raise HTTPException(status_code=400, detail="Se requiere un motivo para detener el trabajo.")
    if nuevo_estado == "en trabajo" and not estado_update.tecnico_id:
        raise HTTPException(status_code=400, detail="Se requiere asignar un técnico para pasar el trabajo a 'en trabajo'.")

    if estado_update.tecnico_id:
        tecnico = db.query(models.Tecnico).filter(models.Tecnico.id == estado_update.tecnico_id).first()
        if not tecnico:
            raise HTTPException(status_code=404, detail="Técnico no encontrado.")
        trabajo_db.tecnico_id = estado_update.tecnico_id
        
    historial_anterior = db.query(models.HistorialDeEstado).filter(
        models.HistorialDeEstado.trabajo_id == trabajo_id, models.HistorialDeEstado.fecha_fin == None
    ).first()
    if historial_anterior:
        historial_anterior.fecha_fin = datetime.datetime.utcnow()
        if historial_anterior.estado == 'agendado' and not trabajo_db.fecha_llegada_taller:
            trabajo_db.fecha_llegada_taller = datetime.datetime.utcnow()
            
    nuevo_historial = models.HistorialDeEstado(
        trabajo_id=trabajo_id, estado=nuevo_estado, motivo_detencion=estado_update.motivo_detencion,
        detalle_motivo=estado_update.detalle_motivo, fecha_eta=estado_update.fecha_eta
    )
    db.add(nuevo_historial)
    trabajo_db.estado_actual = nuevo_estado
    
    db.commit()
    db.refresh(trabajo_db)
    return trabajo_db

@router.get("/{trabajo_id}/historial", response_model=List[schemas.Historial])
def leer_historial_trabajo(
    trabajo_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    trabajo = db.query(models.Trabajo).filter(models.Trabajo.id == trabajo_id).first()
    if not trabajo:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    return sorted(trabajo.historial, key=lambda x: x.fecha_inicio)

@router.post("/upload-excel/", response_model=schemas.UploadResponse, status_code=status.HTTP_201_CREATED)
async def cargar_trabajos_desde_excel(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de archivo inválido. Se requiere .xlsx o .xls")
    
    contenido_bytes = await file.read()
    
    try:
        df_temp = pd.read_excel(io.BytesIO(contenido_bytes), header=None, engine=None)
        header_row_index = -1
        for i, row in df_temp.head(10).iterrows():
            if 'Pedido DBM' in row.values:
                header_row_index = i
                break
        
        if header_row_index == -1:
            raise HTTPException(status_code=422, detail="No se pudo encontrar la fila de encabezado. Asegúrate que la columna 'Pedido DBM' exista.")

        df = pd.read_excel(io.BytesIO(contenido_bytes), header=header_row_index, engine=None)

    except Exception as e:
        logger.error(f"Error al leer o procesar el Excel: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No se pudo leer el archivo Excel: {e}")

    column_mapping = {
        'Pedido DBM': 'pedido_dbm',
        'Motivo de pedido': 'tipo_pedido',
        'Fecha documento': 'fecha_creacion_pedido',
        'Nombre consultor técnico': 'asesor_servicio',
        'Matr.vehículo': 'patente',
        'Sector': 'marca',
        'Descripción del modelo de vehículo': 'modelo_vehiculo',
        'Nº identificación vehículo': 'vin',
        'Nombre del cliente': 'cliente_nombre',
        'Descripción de tarea': 'detalle_pedido',
        'Valor neto': 'total_pedido'
    }

    missing_cols = [col for col in column_mapping.keys() if col not in df.columns]
    if missing_cols:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Faltan las siguientes columnas en el Excel: {', '.join(missing_cols)}")

    df.rename(columns=column_mapping, inplace=True)
    
    date_columns = ['fecha_creacion_pedido']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df[col] = df[col].apply(lambda x: x.to_pydatetime() if pd.notna(x) else None)
    
    df['pedido_dbm'] = pd.to_numeric(df['pedido_dbm'], errors='coerce')
    if 'total_pedido' in df.columns:
        df['total_pedido'] = pd.to_numeric(df['total_pedido'], errors='coerce')

    df.dropna(subset=['pedido_dbm'], inplace=True)
    df['pedido_dbm'] = df['pedido_dbm'].astype(int)

    trabajos_creados, trabajos_actualizados = 0, 0
    db_model_columns = {c.name for c in inspect(models.Trabajo).c}

    for index, row in df.iterrows():
        try:
            pedido_dbm_str = str(row['pedido_dbm'])
            datos_trabajo = {key: value for key, value in row.items() if key in db_model_columns and pd.notna(value)}
            trabajo_existente = db.query(models.Trabajo).filter(models.Trabajo.pedido_dbm == pedido_dbm_str).first()
            if trabajo_existente:
                for key, value in datos_trabajo.items():
                    setattr(trabajo_existente, key, value)
                trabajos_actualizados += 1
            else:
                nuevo_trabajo = models.Trabajo(**datos_trabajo, estado_actual="agendado")
                db.add(nuevo_trabajo)
                db.flush()
                historial_inicial = models.HistorialDeEstado(trabajo_id=nuevo_trabajo.id, estado="agendado")
                db.add(historial_inicial)
                trabajos_creados += 1
        except Exception as e:
            db.rollback()
            logger.error(f"Error procesando fila {index + 2}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Error en la fila {index + 2} del Excel. Detalle: {e}")
    db.commit()
    return {"mensaje": "Archivo procesado exitosamente", "creados": trabajos_creados, "actualizados": trabajos_actualizados}