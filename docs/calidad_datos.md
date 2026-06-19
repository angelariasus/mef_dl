# Gestión de Calidad de Datos (Data Quality)

El aseguramiento de la calidad es una etapa crítica que se ejecuta durante el procesamiento de la Capa Silver. No borramos datos malos de manera arbitraria; en su lugar, aplicamos **DQ Flags** (Banderas de Calidad de Datos).

Las banderas son columnas booleanas o enteras (0 o 1) que indican si un registro infringe ciertas lógicas de negocio, permitiendo al analista decidir si filtra o investiga esos casos atípicos en la Capa Gold o en sus tableros.

## DQ Flags del SIAF

En el notebook `01_silver_siaf.ipynb`, se aplican 12 banderas de calidad a nivel de registro:

| DQ Flag | Descripción y Lógica |
|---------|---------------------|
| `DQ_NEG_PIA` | Verifica si el Presupuesto Inicial (PIA) reportado es menor a 0. |
| `DQ_PIM_LT_PIA` | Verifica si el Presupuesto Modificado (PIM) es menor al Inicial (lo cual es atípico). |
| `DQ_NEG_PIM` | Verifica si el PIM es negativo. |
| `DQ_NEG_REC` | Verifica si el monto recaudado/ejecutado es menor a 0. |
| `DQ_HIGH_RATIO` | Verifica si el monto Recaudado sobrepasa desproporcionadamente (> 200%) al presupuesto PIM. |
| `DQ_ABSURD_AMOUNT` | Detecta montos absurdos (mayores a 50,000 millones de soles) que suelen deberse a errores de digitación en la fuente. |
| `DQ_INCOMPLETE_RECORD` | Identifica filas a las que les faltan campos clave (Nivel gobierno, ejecutora, fuente de financiamiento). |
| `DQ_INVALID_GOV_LEVEL` | El nivel de gobierno no pertenece a los oficiales (E=Nacional, R=Regional, M=Municipal). |
| `DQ_INVALID_FUNDING` | Código de fuente de financiamiento desconocido (fuera del rango oficial 1-9). |
| `DQ_INVALID_GEOGRAPHY` | El código de UBIGEO no cumple con el formato oficial de 6 dígitos numéricos. |
| `DQ_BROKEN_HIERARCHY` | Rompimiento de jerarquía administrativa (ej: existe la ejecutora pero falta el código del pliego principal). |
| `DQ_CATALOG_MISMATCH` | Anomalía donde un mismo código de catálogo tiene registradas múltiples descripciones de texto diferentes. |

## Limpieza General

Antes de aplicar las banderas, el pipeline realiza limpiezas universales:
- **Ghost Nulls**: Se identifican y convierten falsos valores nulos enviados por las APIs del MEF (ej: cadenas `"null"`, `"None"`, `""`, `"N/A"`) a `NULL` reales de Spark.
- **Normalización Geo**: Las mancomunidades y registros sin ubicación geográfica asignada se fuerzan al UBIGEO `"000000"`.
