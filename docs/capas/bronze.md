# Capa Bronze (Ingesta)

La Capa Bronze es el punto de entrada al MEF Data Lake. Su responsabilidad exclusiva es **extraer** la información desde las fuentes externas y **almacenarla localmente** en su estado más crudo y original posible. No se realiza ninguna modificación, limpieza ni cálculo lógico sobre los datos.

## Mecanismos de Extracción

El proceso de extracción es controlado por el módulo Python ubicado en `src/bronze/`. 
Las extracciones están definidas en `src/bronze/config.py`, donde existen 3 tipos de clientes integrados:

1. **CKAN Client (API REST)**: 
   - Utilizado para extraer la data dinámica del **SIAF** y **SISMEPRE**.
   - Consume endpoints de la plataforma de datos abiertos (CKAN) de forma paginada para no sobrecargar los servidores del gobierno.
   - Tiene protección de límite de tiempo, control de reintentos y verificaciones para descargar únicamente si la fuente ha sido actualizada remotamente (evitando re-descargas inútiles).

2. **ZIP Client**:
   - Descarga conjuntos de datos estáticos y pesados empaquetados en `.zip` que ofrece el INEI para el dataset del **RENAMU**.
   - Se encarga de descargar, extraer en memoria y guardar el CSV subyacente.

## Formato de Almacenamiento

Los archivos descargados por las APIs se guardan como **Archivos NDJSON** (Newline Delimited JSON).
Cada archivo se nombra como `batch_0000X.json` dentro de la carpeta correspondiente a la fuente y el año en `data/bronze/`.

**Ejemplo de estructura de directorios:**
```
data/
└── bronze/
    ├── siaf/
    │   ├── 2022/
    │   │   ├── batch_00000.json
    │   │   └── batch_00001.json
    │   └── 2023/
    ├── sismepre/
    │   └── maestro_proyectos/
    │       └── batch_00000.json
    └── renamu/
        └── 2022/
            └── batch_00000.json
```

## Ejecución de la Ingesta

La orquestación principal de esta capa puede ejecutarse desde Jupyter mediante el notebook de ingesta:

```text
notebooks/00_bronze_ingestion.ipynb
```

El script es idempotente; lleva un control interno de qué archivos ya han sido descargados basándose en los metadatos de las APIs gubernamentales.
