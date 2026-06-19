# Usar la imagen oficial y preconfigurada de Jupyter con PySpark
FROM jupyter/pyspark-notebook:latest

# Cambiar a usuario root temporalmente si requerimos configurar dependencias de OS
USER root

# Instalar herramientas útiles si es necesario
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de dependencias de Python del proyecto
COPY requirements.txt /tmp/requirements.txt

# Regresar al usuario por defecto de Jupyter
USER ${NB_UID}

# Instalar los paquetes adicionales (requests, python-dotenv, etc.)
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Configurar el directorio de trabajo
WORKDIR /workspace
