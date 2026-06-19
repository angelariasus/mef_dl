# MEF Data Lake — Arquitectura PySpark

Pipeline ETL completo para datos presupuestales del MEF (Perú) usando PySpark en modo local sobre Jupyter Notebooks.

## Arquitectura Medallion

```
data/bronze/   ← JSON crudos (producidos por notebooks/00_bronze_ingestion.ipynb)
data/silver/   ← Parquet curados por fuente
data/gold/     ← Parquet del modelo dimensional (Star Schema)
```

## Documentación Oficial

Toda la arquitectura, flujos y validaciones de datos se encuentran detallados en el directorio [`/docs`](docs/index.md):
- [1. Arquitectura y Diseño](docs/arquitectura.md)
- [2. Capa Bronze (Ingesta)](docs/capas/bronze.md)
- [3. Capa Silver (Limpieza y Curación)](docs/capas/silver.md)
- [4. Capa Gold (Modelado Dimensional)](docs/capas/gold.md)
- [5. Calidad de Datos (DQ)](docs/calidad_datos.md)

## Fuentes de Datos


| Fuente | Método | Destino Bronze |
|--------|--------|----------------|
| SIAF | API CKAN paginada / ZIP histórico | `bronze/siaf/{año}/` |
| SISMEPRE (7 tablas) | API CKAN | `bronze/sismepre/{tabla}/` |
| RENAMU | ZIP (INEI) | `bronze/renamu/2022/` |

## Flujo de Ejecución

1. **Ingesta Bronze**: Ejecutar `notebooks/00_bronze_ingestion.ipynb`
2. **Silver SIAF**: Ejecutar `notebooks/01_silver_siaf.ipynb`
3. **Silver SISMEPRE**: Ejecutar `notebooks/02_silver_sismepre.ipynb`
4. **Silver RENAMU**: Ejecutar `notebooks/03_silver_renamu.ipynb`
5. **Gold SIAF**: Ejecutar `notebooks/04_gold_siaf.ipynb`
6. **Gold SISMEPRE**: Ejecutar `notebooks/05_gold_sismepre.ipynb`
7. **Gold RENAMU**: Ejecutar `notebooks/06_gold_renamu.ipynb`

## Setup y Ejecución

Tienes dos opciones para levantar el entorno del Data Lake: usando Docker (recomendado para no lidiar con instalaciones) o usando un entorno virtual local.

### Opción 1: Usando Docker (Recomendada)
Esta opción ya trae integrado Python, PySpark, Jupyter y todas las librerías configuradas (con 6GB de memoria para Spark). **No necesitas crear `.venv` ni instalar `requirements` en tu PC.**

```bash
# 1. (Opcional) Copiar variables de entorno
cp .env.example .env

# 2. Levantar el contenedor
docker-compose up -d --build

# 3. Ingresar a Jupyter Lab
# Abre tu navegador en: http://localhost:8101
# Contraseña / Token: desarrollo
```

### Opción 2: Usando Entorno Local
Útil si prefieres usar tu propia instalación de Spark de tu sistema operativo o si solo quieres que VS Code te dé autocompletado de código.

```bash
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar el entorno virtual
# En Windows:
.venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
cp .env.example .env

# 4. Levantar Jupyter Lab
jupyter lab
```
