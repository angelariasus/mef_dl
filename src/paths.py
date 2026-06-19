"""
Rutas del proyecto MEF DW v2.
Fuente única de verdad para todos los paths de datos en el proyecto.
Importar desde los notebooks: from src.paths import BRONZE, SILVER, GOLD, STATIC
"""
from pathlib import Path

# Raíz del proyecto (src/ → mef_dw_v2/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Capa de datos base
DATA_ROOT = PROJECT_ROOT / "data"

# ── Bronze — Datos crudos JSON ────────────────────────────────────────────────
BRONZE = {
    "siaf":     DATA_ROOT / "bronze" / "siaf",
    "sismepre": DATA_ROOT / "bronze" / "sismepre",
    "renamu":   DATA_ROOT / "bronze" / "renamu",
}

# ── Silver — Parquet curados ──────────────────────────────────────────────────
SILVER = {
    "siaf":     DATA_ROOT / "silver" / "siaf",
    "sismepre": DATA_ROOT / "silver" / "sismepre",
    "renamu":   DATA_ROOT / "silver" / "renamu",
}

# ── Gold — Modelo Dimensional Parquet ─────────────────────────────────────────
GOLD = {
    "dim_tiempo":                  DATA_ROOT / "gold" / "dim_tiempo",
    "dim_geografia":               DATA_ROOT / "gold" / "dim_geografia",
    "dim_municipalidad":           DATA_ROOT / "gold" / "dim_municipalidad",
    "dim_clasificacion_ingreso":   DATA_ROOT / "gold" / "dim_clasificacion_ingreso",
    "dim_financiamiento":          DATA_ROOT / "gold" / "dim_financiamiento",
    "fact_ejecucion_presupuestal": DATA_ROOT / "gold" / "fact_ejecucion_presupuestal",
    # SISMEPRE
    "sismepre_formulario":         DATA_ROOT / "gold" / "sismepre_formulario",
    "sismepre_preguntas":          DATA_ROOT / "gold" / "sismepre_preguntas",
    "sismepre_respuestas":         DATA_ROOT / "gold" / "sismepre_respuestas",
    "sismepre_estadistica":        DATA_ROOT / "gold" / "sismepre_estadistica",
    "sismepre_esat_atm":           DATA_ROOT / "gold" / "sismepre_esat_atm",
    "sismepre_entidad_estado":     DATA_ROOT / "gold" / "sismepre_entidad_estado",
    "sismepre_ano_aplicacion":     DATA_ROOT / "gold" / "sismepre_ano_aplicacion",
    # RENAMU
    "stg_renamu":                  DATA_ROOT / "gold" / "stg_renamu",
}

# ── Archivos estáticos ────────────────────────────────────────────────────────
STATIC = DATA_ROOT / "static"
CATEGORIAS_CSV = STATIC / "categorias_clean.csv"

# ── Auditoría ─────────────────────────────────────────────────────────────────
AUDIT_DIR = DATA_ROOT / "audit" / "executions"
STATE_FILE = DATA_ROOT / ".state.json"


def ensure_dirs() -> None:
    """Crea toda la estructura de directorios si no existe."""
    all_paths = (
        list(BRONZE.values())
        + list(SILVER.values())
        + list(GOLD.values())
        + [STATIC, AUDIT_DIR]
    )
    for p in all_paths:
        p.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Estructura de directorios verificada en {DATA_ROOT}")


def str_path(p: Path) -> str:
    """Convierte Path a string con barras forward (compatible con Spark)."""
    return str(p).replace("\\", "/")
