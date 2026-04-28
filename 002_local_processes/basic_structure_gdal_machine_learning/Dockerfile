# STAGE 1: Builder (Compilación de GDAL y Dependencias)
FROM nvidia/cuda:12.3.1-devel-ubuntu22.04 AS builder

# Configurar variables para no interactivo
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias de compilación completas para GDAL y Python
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgdal-dev \
    python3-dev \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Configurar variables de entorno críticas para la compilación de Rasterio/GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Crear entorno virtual estándar en /opt/venv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Actualizar herramientas de compilación base de Python
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Construir todo el entorno de Python en el venv usando las wheels oficiales
RUN pip install --no-cache-dir torch torchvision torchaudio typer geopandas torchgeo rasterio

# STAGE 2: Runtime (Imagen Final Ligera)
FROM nvidia/cuda:12.3.1-runtime-ubuntu22.04

# Instalar solo las librerías de sistema mínimas requeridas por las wheels
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Copiar el entorno virtual del Stage 1
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Configurar variables de entorno puramente de Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app
COPY . .

# Comando por defecto definido en docker-compose
CMD ["python3", "src/main.py"]
