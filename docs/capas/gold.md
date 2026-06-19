# Capa Gold (Modelado Dimensional)

La Capa Gold es el producto final del Data Lake. Su principal objetivo es organizar y relacionar los datos para entregarlos a herramientas de BI (Business Intelligence) o para servir a modelos de analítica avanzada.

La orquestación se realiza mediante los notebooks `04_gold_siaf.ipynb`, `05_gold_sismepre.ipynb` y `06_gold_renamu.ipynb`.

## Enfoques de Modelado por Dominio

Debido a la naturaleza disímil de las fuentes (financiero, administrativo y macroeconómico), se utilizan diferentes patrones de modelado para cada área.

### 1. Modelo SIAF (Star Schema Tradicional)
El SIAF concentra métricas altamente transaccionales (Presupuesto PIA, PIM, Recaudado).
Para este modelo, se generó un esquema de estrella puro:
- **Tabla de Hechos (Fact_SIAF)**: Particionada por año. Contiene las llaves foráneas (SKs) e importes numéricos.
- **Dimensiones (Dim_*)**: `Dim_Tiempo`, `Dim_Geografia` (construida a partir de ubigeos oficiales en el catálogo `categorias.csv`), `Dim_Financiamiento` y `Dim_Rubro`.

### 2. Modelo RENAMU (Modelo EAV / Unpivot)
El Registro Nacional de Municipalidades es un dataset ancho con más de 1,300 columnas, cada una representando una pregunta específica (ej: "¿Tiene plan de seguridad?", "¿Número de computadoras?").
En la capa Gold, este dataset se transforma utilizando la técnica **Entity-Attribute-Value (EAV)** (o _unpivot_):
- En lugar de 1,300 columnas, el modelo Gold resultante tiene las columnas: `ANO_RENAMU`, `UBIGEO`, `VARIABLE_NAME`, `VALUE`.
- Esta estructura es infinitamente más amigable para un motor analítico a la hora de buscar preguntas sin necesidad de escanear la tabla entera a lo ancho.

### 3. Modelo SISMEPRE (Desnormalizado / OBT)
Los datos de inversión pública no requieren una dimensionalidad extensa debido a su volumen acotado y uso específico.
El enfoque es construir una "One Big Table" (OBT) donde todas las llaves (nombres de fase, estado, etc.) están materializadas directamente en la tabla principal, lista para filtrados rápidos sin JOINs.

## Exportación

El resultado final se encuentra en `data/gold/`. 
Todas las tablas se guardan como archivos **Parquet**, listos para ser consumidos directamente por librerías exploratorias en Python (Pandas/Polars), o leídas por herramientas de BI empresariales que soporten este formato.
