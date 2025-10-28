# schemas.py

from pydantic import BaseModel, ConfigDict
import datetime
from typing import Optional, List, Any

# --- ESQUEMAS DE TECNICO (CORRECTOS) ---
class TecnicoBase(BaseModel):
    codigo: str
    nombre_completo: str

class TecnicoCreate(TecnicoBase):
    pass

class Tecnico(TecnicoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- ESQUEMAS EXISTENTES (CON CORRECCIÓN) ---

class HistorialBase(BaseModel):
    estado: str

class Historial(HistorialBase):
    id: int
    fecha_inicio: datetime.datetime
    fecha_fin: Optional[datetime.datetime] = None
    motivo_detencion: Optional[str] = None
    detalle_motivo: Optional[str] = None
    fecha_eta: Optional[datetime.datetime] = None
    model_config = ConfigDict(from_attributes=True)

class TrabajoBase(BaseModel):
    pedido_dbm: str
    estado_pedido: Optional[str] = None
    fecha_creacion_pedido: Optional[datetime.datetime] = None
    fecha_cierre_pedido: Optional[datetime.datetime] = None
    cliente_nombre: Optional[str] = None
    patente: Optional[str] = None
    marca: Optional[str] = None
    modelo_vehiculo: Optional[str] = None
    vin: Optional[str] = None
    asesor_servicio: Optional[str] = None
    tipo_pedido: Optional[str] = None
    detalle_pedido: Optional[str] = None
    total_pedido: Optional[float] = None
    fecha_llegada_taller: Optional[datetime.datetime] = None

class Trabajo(TrabajoBase):
    id: int
    estado_actual: str
    dias_de_estadia_activa: Optional[int] = 0
    historial: List[Historial] = []
    # --- ✨ CORRECCIÓN AQUÍ ---
    # El nombre debe coincidir con el atributo de la relación en models.py
    tecnico_asignado: Optional[Tecnico] = None
    # -------------------------
    model_config = ConfigDict(from_attributes=True)

class TrabajoUpdateEstado(BaseModel):
    nuevo_estado: str
    motivo_detencion: Optional[str] = None
    detalle_motivo: Optional[str] = None
    fecha_eta: Optional[datetime.datetime] = None
    tecnico_id: Optional[int] = None # <-- Esto está correcto
    
# ... (el resto del archivo es correcto) ...

class TrabajoUpdate(BaseModel):
    detalle_pedido: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class PaginatedTrabajos(BaseModel):
    items: List[Trabajo]
    total: int
    model_config = ConfigDict(from_attributes=True)

class UploadResponse(BaseModel):
    mensaje: str
    creados: int
    actualizados: int
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role: str
    model_config = ConfigDict(from_attributes=True)

class UserSettings(BaseModel):
    column_config: Optional[Any] = None
    model_config = ConfigDict(from_attributes=True)