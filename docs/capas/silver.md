# Capa Silver (Limpieza y Curación)

La Capa Silver toma los archivos de la Capa Bronze, los limpia, los estandariza y los guarda en un formato columnar optimizado para analítica (**Parquet**). 

Toda la orquestación y el procesamiento se realizan utilizando Apache Spark, gestionado visualmente mediante los siguientes notebooks:
- `01_silver_siaf.ipynb`
- `02_silver_sismepre.ipynb`
- `03_silver_renamu.ipynb`

## Transformaciones Clave

En esta capa no se cruzan métricas de negocio con otras tablas (eso pertenece a Gold). El enfoque es asegurar la calidad tabular por cada fuente aislada.

1. **Lectura de Esquemas Explícitos**: Se fuerza un esquema (Schema) explícito al leer los JSON crudos para evitar fallos de inferencia dinámica por parte de Spark.
2. **Casteo de Tipos de Datos**: Transformación de cadenas de texto a enteros, flotantes o fechas reales.
3. **Ghost Nulls**: Conversión de literales anómalos (`"None"`, `"null"`, `"N/A"`) a valores `NULL`.
4. **Normalización Geográfica**: Se extrae, concatena o fuerza un código de `UBIGEO` (código de distrito peruano) uniforme de 6 dígitos que servirá de llave común para las distintas fuentes.
5. **Deduplicación**: Se aplican ventanas lógicas (Window Functions) para limpiar registros duplicados que envían las APIs en sus procesos de paginación.
6. **Data Quality Flags (DQ)**: Se evalúan los registros contra 12 reglas de validación (presupuestos negativos, jerarquías rotas, etc.). Ver [Calidad de Datos](../calidad_datos.md) para los detalles.

## Particionamiento Parquet

Los DataFrames limpios se guardan en el directorio `data/silver/` usando el formato **Apache Parquet**.

Para fuentes muy voluminosas (ej: SIAF con millones de filas o RENAMU por ser archivos pesados anuales), Spark escribe los resultados utilizando particionamiento físico (ej: `partitionBy("ANO_DOC")`). Esto permite que procesos posteriores puedan leer únicamente el año de interés sin levantar el peso de la base histórica completa.
