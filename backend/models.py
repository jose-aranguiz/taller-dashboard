from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Trabajo(Base):
    __tablename__ = "trabajos"

    id = Column(Integer, primary_key=True, index=True)
    
    pedido_dbm = Column(String, unique=True, index=True)
    estado_pedido = Column(String, nullable=True)
    fecha_creacion_pedido = Column(DateTime, nullable=True)
    fecha_cierre_pedido = Column(DateTime, nullable=True)
    cliente_nombre = Column(String, nullable=True)
    patente = Column(String, index=True, nullable=True)
    marca = Column(String, nullable=True)
    modelo_vehiculo = Column(String, nullable=True)
    vin = Column(String, nullable=True)
    asesor_servicio = Column(String, nullable=True)
    # La columna 'tecnico' del excel la dejamos por compatibilidad, pero usaremos la relación para la lógica
    tecnico = Column(String, nullable=True)
    tipo_pedido = Column(String, nullable=True)
    detalle_pedido = Column(Text, nullable=True)
    total_pedido = Column(Float, nullable=True)
    
    estado_actual = Column(String, default="agendado")
    fecha_llegada_taller = Column(DateTime, nullable=True)
    
    historial = relationship("HistorialDeEstado", back_populates="trabajo")
    
    # --- RELACIÓN CON TECNICO ---
    tecnico_id = Column(Integer, ForeignKey("tecnicos.id"), nullable=True)
    tecnico_asignado = relationship("Tecnico", back_populates="trabajos")


class HistorialDeEstado(Base):
    __tablename__ = "historial_de_estados"

    id = Column(Integer, primary_key=True, index=True)
    trabajo_id = Column(Integer, ForeignKey("trabajos.id"))
    estado = Column(String, index=True)
    
    fecha_inicio = Column(DateTime, default=datetime.datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=True)
    
    motivo_detencion = Column(String, nullable=True)
    detalle_motivo = Column(String, nullable=True)
    fecha_eta = Column(DateTime, nullable=True)
    
    trabajo = relationship("Trabajo", back_populates="historial")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
    
    settings = relationship("UserSettings", back_populates="owner", uselist=False)

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    column_config = Column(JSON)
    
    owner = relationship("User", back_populates="settings")

# --- NUEVO MODELO TECNICO ---
class Tecnico(Base):
    __tablename__ = "tecnicos"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True, nullable=False)
    nombre_completo = Column(String, nullable=False)
    
    trabajos = relationship("Trabajo", back_populates="tecnico_asignado")