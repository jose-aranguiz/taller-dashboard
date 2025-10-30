from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Body, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, inspect, select
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any, Tuple
import models, schemas, auth
# 👇 CORRECCIÓN AQUÍ: Importamos get_db
from database import SessionLocal, get_db
import datetime
import pandas as pd
from pandas import DataFrame 
import io
import logging

# ... (el resto del archivo trabajos.py se mantiene exactamente igual que en el Paso 6) ...

# --- Asegúrate de que TODAS las funciones que usan Depends(get_db) ---
# --- estén DESPUÉS de la línea de importación ---

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VALID_TRANSITIONS = {
    "agendado": ["espera de trabajo"], "espera de trabajo": ["en trabajo", "en lavado"],
    "en trabajo": ["trabajo detenido", "control de calidad", "en lavado"], "trabajo detenido": ["en trabajo"],
    "en lavado": ["espera de trabajo", "en trabajo", "control de calidad"], "control de calidad": ["listo para entrega", "en trabajo"],
    "listo para entrega": ["entregado al cliente"], "entregado al cliente": []
}

COLUMN_MAPPING = {
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

router = APIRouter(prefix="/trabajos", tags=["Trabajos"])

# get_db() ya está importado, por lo que las siguientes funciones 
# que usan Depends(get_db) deberían funcionar.

@router.get("/", response_model=schemas.PaginatedTrabajos)
def leer_trabajos_paginados(
    db: Session = Depends(get_db), # <- Ahora get_db está definido
    page: int = 1,
    limit: int = 15,
    sort_by: Optional[str] = "id",
    sort_order: str = "desc",
    search: Optional[str] = None,
    asesor_servicio: Optional[str] = None,
    estado_actual: Optional[str] = Query(None),
    fecha_desde: Optional[datetime.date] = Query(None),
    fecha_hasta: Optional[datetime.date] = Query(None),
    activos: bool = True,
    patente: Optional[str] = None,
    current_user: schemas.User = Depends(auth.get_current_active_user) # Usa la dependencia correcta
):
    try:
        tiempo_detenido_subquery = (
            select(
                func.sum(
                    func.extract(
                        "epoch",
                        func.coalesce(models.HistorialDeEstado.fecha_fin, func.now()) - models.HistorialDeEstado.fecha_inicio
                    )
                )
            )
            .where(
                models.HistorialDeEstado.trabajo_id == models.Trabajo.id,
                models.HistorialDeEstado.estado == 'trabajo detenido'
            )
            .correlate(models.Trabajo) 
            .as_scalar()
        )

        query = db.query(
            models.Trabajo,
            func.coalesce(tiempo_detenido_subquery, 0).label("tiempo_detenido_segundos")
        )

        if patente:
            query = query.filter(models.Trabajo.patente.ilike(f"%{patente}%")).order_by(models.Trabajo.fecha_creacion_pedido.desc())
        else:
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

        total_records = query.count()

        if sort_by and hasattr(models.Trabajo, sort_by):
            columna_a_ordenar = getattr(models.Trabajo, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(columna_a_ordenar.desc())
            else:
                query = query.order_by(columna_a_ordenar.asc())
        
        offset = (page - 1) * limit
        items_con_tiempo = query.offset(offset).limit(limit).all()
        
        items = [] 
        for trabajo, tiempo_detenido_segundos in items_con_tiempo:
            try:
                fecha_inicio_conteo = trabajo.fecha_llegada_taller or trabajo.fecha_creacion_pedido
                if not fecha_inicio_conteo:
                    trabajo.dias_de_estadia_activa = 0
                    items.append(trabajo)
                    continue

                if hasattr(fecha_inicio_conteo, 'tzinfo') and fecha_inicio_conteo.tzinfo is not None:
                    fecha_inicio_conteo = fecha_inicio_conteo.replace(tzinfo=None)

                tiempo_total_segundos = (datetime.datetime.utcnow() - fecha_inicio_conteo).total_seconds()
                tiempo_activo_segundos = tiempo_total_segundos - tiempo_detenido_segundos
                trabajo.dias_de_estadia_activa = int(tiempo_activo_segundos / (24 * 3600)) if tiempo_activo_segundos > 0 else 0
            
            except Exception as e:
                logger.error(f"Error calculando días de estadía para trabajo ID {trabajo.id}: {e}")
                trabajo.dias_de_estadia_activa = -1
            
            items.append(trabajo) 

        return {"items": items, "total": total_records}

    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos en leer_trabajos_paginados: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error de base de datos al consultar trabajos.")
    except Exception as e:
        logger.error(f"Error inesperado en leer_trabajos_paginados: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ocurrió un error inesperado en el servidor al listar los trabajos.")


@router.patch("/{trabajo_id}", response_model=schemas.Trabajo)
def actualizar_trabajo(
    trabajo_id: int, 
    trabajo_update: schemas.TrabajoUpdate, 
    db: Session = Depends(get_db), # <- Ahora get_db está definido
    current_user: schemas.User = Depends(auth.get_current_active_user)
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
    db: Session = Depends(get_db), # <- Ahora get_db está definido
    current_user: schemas.User = Depends(auth.get_current_active_user)
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
    db: Session = Depends(get_db), # <- Ahora get_db está definido
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    trabajo = db.query(models.Trabajo).filter(models.Trabajo.id == trabajo_id).first()
    if not trabajo:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    # Aseguramos que historial sea una lista antes de ordenar
    historial = trabajo.historial if trabajo.historial else []
    return sorted(historial, key=lambda x: x.fecha_inicio)


# --- Funciones auxiliares de carga de Excel ---
# ... (Estas funciones _buscar_fila_encabezado, _validar_y_renombrar_columnas, etc. se mantienen igual) ...

def _buscar_fila_encabezado(df_temp: DataFrame) -> int:
    for i, row in df_temp.head(10).iterrows():
        if 'Pedido DBM' in row.values:
            return i
    return -1

def _validar_y_renombrar_columnas(df: DataFrame) -> DataFrame:
    missing_cols = [col for col in COLUMN_MAPPING.keys() if col not in df.columns]
    if missing_cols:
        logger.error(f"Faltan columnas en el Excel: {missing_cols}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Faltan las siguientes columnas en el Excel: {', '.join(missing_cols)}")
    
    df.rename(columns=COLUMN_MAPPING, inplace=True)
    return df

def _limpiar_dataframe(df: DataFrame) -> DataFrame:
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
    return df

def _procesar_filas_dataframe(db: Session, df: DataFrame) -> Tuple[int, int]:
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
            logger.error(f"Error procesando fila {index + 2}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail=f"Error en la fila {index + 2} del Excel (Pedido DBM: {row.get('pedido_dbm', 'N/A')}). Detalle: {e}"
            )
            
    return trabajos_creados, trabajos_actualizados

# Ruta principal de carga de Excel
@router.post("/upload-excel/", response_model=schemas.UploadResponse, status_code=status.HTTP_201_CREATED)
async def cargar_trabajos_desde_excel(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), # <- Ahora get_db está definido
    current_user: schemas.User = Depends(auth.get_current_admin_user) # <- Usa la dependencia correcta de admin
):
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de archivo inválido. Se requiere .xlsx o .xls")
    
    contenido_bytes = await file.read()
    
    try:
        df_temp = pd.read_excel(io.BytesIO(contenido_bytes), header=None, engine=None)
        header_row_index = _buscar_fila_encabezado(df_temp)
        
        if header_row_index == -1:
            raise HTTPException(status_code=422, detail="No se pudo encontrar la fila de encabezado. Asegúrate que la columna 'Pedido DBM' exista.")

        df = pd.read_excel(io.BytesIO(contenido_bytes), header=header_row_index, engine=None)

    except Exception as e:
        logger.error(f"Error al leer o procesar el Excel: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No se pudo leer el archivo Excel: {e}")

    df = _validar_y_renombrar_columnas(df)
    df = _limpiar_dataframe(df)

    try:
        trabajos_creados, trabajos_actualizados = _procesar_filas_dataframe(db, df)
        db.commit()
        
    except (SQLAlchemyError, HTTPException) as e:
        db.rollback()
        logger.error(f"Error al procesar las filas del DataFrame y guardar en BBDD: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error de base de datos durante el procesamiento: {e}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al procesar filas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error inesperado al procesar filas: {e}")

    return {"mensaje": "Archivo procesado exitosamente", "creados": trabajos_creados, "actualizados": trabajos_actualizados}