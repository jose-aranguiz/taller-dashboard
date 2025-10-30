# 1. Usar una imagen oficial de Python como base
# 👇 CORRECCIÓN: Usar una versión de Python que soporte la sintaxis moderna (3.10+)
FROM python:3.10-slim

# --- SECCIÓN AÑADIDA ---
# Instalar dependencias de compilación para psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar el archivo de requerimientos
COPY requirements.txt .

# 4. Instalar todas las librerías necesarias
RUN pip install -r requirements.txt

# 5. COPIAR TODO EL CÓDIGO DE LA APP AL CONTENEDOR
COPY . .

# 6. Comando para ejecutar la aplicación cuando el contenedor se inicie
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]