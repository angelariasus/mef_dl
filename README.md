# MEF Data Lake v2 — Arquitectura Vanilla PySpark

Pipeline ETL completo para datos presupuestales del MEF (Perú) usando PySpark en modo local sobre Jupyter Notebooks, sin dependencias de SQL, AWS ni orquestadores externos.

## Arquitectura Medallion

```
data/bronze/   ← JSON crudos (producidos por bronze/ingest_bronze.py)
data/silver/   ← Parquet curados por fuente
data/gold/     ← Parquet del modelo dimensional (Star Schema)
```

## Fuentes de Datos

| Fuente | Método | Destino Bronze |
|--------|--------|----------------|
| SIAF | API CKAN paginada / ZIP histórico | `bronze/siaf/{año}/` |
| SISMEPRE (7 tablas) | API CKAN | `bronze/sismepre/{tabla}/` |
| RENAMU | ZIP (INEI) | `bronze/renamu/2022/` |

## Flujo de Ejecución

1. **Ingesta Bronze**: `python -m bronze.ingest_bronze`
2. **Silver SIAF**: Ejecutar `notebooks/01_silver_siaf.ipynb`
3. **Silver SISMEPRE**: Ejecutar `notebooks/02_silver_sismepre.ipynb`
4. **Silver RENAMU**: Ejecutar `notebooks/03_silver_renamu.ipynb`
5. **Gold SIAF**: Ejecutar `notebooks/04_gold_siaf.ipynb`
6. **Gold SISMEPRE**: Ejecutar `notebooks/05_gold_sismepre.ipynb`
7. **Gold RENAMU**: Ejecutar `notebooks/06_gold_renamu.ipynb`

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Editar .env si es necesario
jupyter lab
```
