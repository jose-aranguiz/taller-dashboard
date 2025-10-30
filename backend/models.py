from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import datetime
from database import Base # Asegúrate de importar Base

# --- Modelo de Usuario ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user") # 'user' o 'admin'

# --- Modelo de Técnico ---
class Tecnico(Base):
    __tablename__ = "tecnicos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, unique=True)
    
    # --- 👇 RELACIÓN AÑADIDA ---
    # Un técnico puede tener muchos trabajos. 'back_populates' conecta con 'tecnico_asignado' en Trabajo
    trabajos_asignados = relationship("Trabajo", back_populates="tecnico_asignado")

# --- Modelo de Trabajo ---
class Trabajo(Base):
    __tablename__ = "trabajos"
    id = Column(Integer, primary_key=True, index=True)
    pedido_dbm = Column(String, unique=True, index=True)
    tipo_pedido = Column(String)
    fecha_creacion_pedido = Column(DateTime(timezone=True), default=func.now())
    asesor_servicio = Column(String, index=True)
    patente = Column(String, index=True)
    marca = Column(String)
    modelo_vehiculo = Column(String)
    vin = Column(String, index=True)
    cliente_nombre = Column(String, index=True)
    detalle_pedido = Column(Text)
    total_pedido = Column(Float)
    
    estado_actual = Column(String, default="agendado", index=True)
    fecha_llegada_taller = Column(DateTime(timezone=True), nullable=True)
    
    eta_fecha = Column(DateTime(timezone=True), nullable=True) # Para 'trabajo detenido'
    eta_motivo = Column(String, nullable=True) # Para 'trabajo detenido'
    
    # --- 👇 RELACIÓN ACTUALIZADA ---
    tecnico_id = Column(Integer, ForeignKey("tecnicos.id"), nullable=True)
    # Conecta con 'trabajos_asignados' en Tecnico
    tecnico_asignado = relationship("Tecnico", back_populates="trabajos_asignados") 

    # Un trabajo tiene muchos historiales
    historial = relationship("HistorialDeEstado", back_populates="trabajo")

# --- Modelo de Historial de Estado ---
class HistorialDeEstado(Base):
    __tablename__ = "historial_de_estados"
    id = Column(Integer, primary_key=True, index=True)
    trabajo_id = Column(Integer, ForeignKey("trabajos.id"))
    estado = Column(String, nullable=False)
    fecha_inicio = Column(DateTime(timezone=True), server_default=func.now())
    fecha_fin = Column(DateTime(timezone=True), nullable=True)
    
    # Campos para estado 'detenido'
    motivo_detencion = Column(String, nullable=True)
    detalle_motivo = Column(String, nullable=True)
    fecha_eta = Column(DateTime(timezone=True), nullable=True) # ETA específica de esta detención

    # Relación inversa
    trabajo = relationship("Trabajo", back_populates="historial")