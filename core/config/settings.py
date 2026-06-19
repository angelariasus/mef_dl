import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv

# Raíz del proyecto: settings.py -> config/ -> core/ -> mef_dw/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=True)

# ── Mapeo de Resource IDs por año (SIAF) ──────────────────────────────────────
# Cada año en la API del MEF tiene su propio resource_id.
# Fuente: Portal datosabiertos.mef.gob.pe
SIAF_RESOURCE_IDS: Dict[int, str] = {
    2022: "031bc35d-f6e6-48ef-8aed-8df6c23b7a7a",
    2023: "aee29919-51e9-4aad-b3fa-a474ea1a7292",
    2024: "228c2d8b-f58f-435c-bf96-c7556e8c537d",
    2025: "93c5ce61-e16c-4165-89c8-ac293422bd97",
    2026: "534994e6-2422-4e3e-97aa-bb56acb80c97",
}

# URLs del portal para scraping de fecha de última actualización
_SIAF_SLUG = "presupuesto-y-ejecucion-de-ingreso"
_PORTAL_URL = "https://datosabiertos.mef.gob.pe"
SIAF_PAGE_URLS: Dict[int, str] = {
    2022: f"{_PORTAL_URL}/dataset/{_SIAF_SLUG}/resource/031bc35d-f6e6-48ef-8aed-8df6c23b7a7a",
    2023: f"{_PORTAL_URL}/dataset/{_SIAF_SLUG}/resource/aee29919-51e9-4aad-b3fa-a474ea1a7292",
    2024: f"{_PORTAL_URL}/dataset/{_SIAF_SLUG}/resource/228c2d8b-f58f-435c-bf96-c7556e8c537d",
    2025: f"{_PORTAL_URL}/dataset/{_SIAF_SLUG}/resource/93c5ce61-e16c-4165-89c8-ac293422bd97",
    2026: f"{_PORTAL_URL}/dataset/{_SIAF_SLUG}/resource/534994e6-2422-4e3e-97aa-bb56acb80c97",
}

# URLs para descargar SIAF histórico mediante ZIP
SIAF_ZIP_URLS: Dict[int, str] = {
    year: f"https://fs.datosabiertos.mef.gob.pe/datastorefiles/{year}-Ingreso.zip"
    for year in range(2012, 2025)
}
SIAF_ZIP_URLS[2025] = "https://fs.datosabiertos.mef.gob.pe/datastorefiles/2025-Ingreso-Diario.zip"
SIAF_ZIP_URLS[2026] = "https://fs.datosabiertos.mef.gob.pe/datastorefiles/2026-Ingreso-Diario.zip"

# ── SISMEPRE ──────────────────────────────────────────────────────────────────
# Las 7 tablas del modelo relacional de Rentas del SISMEPRE (sin diccionarios)
SISMEPRE_RESOURCE_IDS: Dict[str, str] = {
    # Tablas originalmente integradas
    "RENTAS_ESAT_ESTADISTICA_ATM": "52f97ee4-6a52-465a-98e8-7e5ba8328b30",
    "RENTAS_ENTIDAD_ESTADO":       "5989e884-f198-4a92-817d-890d71e8984a",
    "RENTAS_FORMULARIO":           "5473b6da-2453-48d0-bc50-e38afc8e732c",
    # Tablas adicionales completando el modelo
    "RENTAS_PREGUNTAS":            "96b53d87-dc98-41ee-8fea-3b45e6201942",
    "RENTAS_ESTADISTICA":          "69abaf52-1d36-4efb-86d0-38af739896c7",
    "RENTAS_RESPUESTAS":           "d03c11b0-3c33-4c61-85fc-507bbcaf9cae",
    "RENTAS_ANO_APLICACION":       "d107f21c-686a-4217-ac0c-9f96b4f00df0",
}

_SISMEPRE_SLUG = "seguimiento-de-la-meta-del-impuesto-predial"
SISMEPRE_PAGE_URLS: Dict[str, str] = {
    "RENTAS_ESAT_ESTADISTICA_ATM": f"{_PORTAL_URL}/dataset/{_SISMEPRE_SLUG}/resource/52f97ee4-6a52-465a-98e8-7e5ba8328b30",
    "RENTAS_ENTIDAD_ESTADO":       f"{_PORTAL_URL}/dataset/{_SISMEPRE_SLUG}/resource/5989e884-f198-4a92-817d-890d71e8984a",
    "RENTAS_FORMULARIO":           f"{_PORTAL_URL}/dataset/{_SISMEPRE_SLUG}/resource/5473b6da-2453-48d0-bc50-e38afc8e732c",
    "RENTAS_PREGUNTAS":            f"{_PORTAL_URL}/dataset/{_SISMEPRE_SLUG}/resource/96b53d87-dc98-41ee-8fea-3b45e6201942",
    "RENTAS_ESTADISTICA":          f"{_PORTAL_URL}/dataset/{_SISMEPRE_SLUG}/resource/69abaf52-1d36-4efb-86d0-38af739896c7",
    "RENTAS_RESPUESTAS":           f"{_PORTAL_URL}/dataset/{_SISMEPRE_SLUG}/resource/d03c11b0-3c33-4c61-85fc-507bbcaf9cae",
    "RENTAS_ANO_APLICACION":       f"{_PORTAL_URL}/dataset/{_SISMEPRE_SLUG}/resource/d107f21c-686a-4217-ac0c-9f96b4f00df0",
}

RENAMU_ZIP_URLS: Dict[int, str] = {
    year: f"https://www.inei.gob.pe/media/DATOS_ABIERTOS/RENAMU/DATA/{year}.zip"
    for year in range(2012, 2025)
}


@dataclass
class Settings:
    """Configuración centralizada del framework MEF DW."""

    # ── API MEF ──────────────────────────────────────────────────────────────
    API_BASE_URL: str = os.getenv(
        "MEF_API_BASE_URL",
        "https://api.datosabiertos.mef.gob.pe/DatosAbiertos/v1",
    )
    RESOURCE_IDS: Dict[int, str] = field(default_factory=lambda: SIAF_RESOURCE_IDS)
    PAGE_URLS: Dict[int, str] = field(default_factory=lambda: SIAF_PAGE_URLS)
    YEARS: List[int] = field(default_factory=lambda: [
        int(y) for y in os.getenv("MEF_YEARS", "2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025,2026").split(",")
    ])
    BATCH_SIZE: int = int(os.getenv("MEF_BATCH_SIZE", "10000"))

    # ── Fuentes Adicionales ──────────────────────────────────────────────────
    SIAF_ZIP_URLS: Dict[int, str] = field(default_factory=lambda: SIAF_ZIP_URLS)
    SISMEPRE_RESOURCE_IDS: Dict[str, str] = field(default_factory=lambda: SISMEPRE_RESOURCE_IDS)
    SISMEPRE_PAGE_URLS: Dict[str, str] = field(default_factory=lambda: SISMEPRE_PAGE_URLS)
    RENAMU_ZIP_URLS: Dict[int, str] = field(default_factory=lambda: RENAMU_ZIP_URLS)

    # ── Rutas de datos ───────────────────────────────────────────────────────
    PROJECT_ROOT: Path = PROJECT_ROOT
    BRONZE_DIR: Path = PROJECT_ROOT / os.getenv("MEF_BRONZE_DIR", "data/bronze")
    SILVER_DIR: Path = PROJECT_ROOT / os.getenv("MEF_SILVER_DIR", "data/silver")
    GOLD_DIR: Path = PROJECT_ROOT / os.getenv("MEF_GOLD_DIR", "data/gold")
    STATE_FILE: Path = PROJECT_ROOT / os.getenv("MEF_STATE_FILE", "data/.state.json")

    SPARK_APP_NAME: str = os.getenv("MEF_SPARK_APP_NAME", "MEF_Pipeline")
    # ── General ──────────────────────────────────────────────────────────────
    MAX_RETRIES: int = int(os.getenv("MEF_MAX_RETRIES", "3"))
    BACKOFF_FACTOR: float = float(os.getenv("MEF_BACKOFF_FACTOR", "2.0"))
    HTTP_TIMEOUT: int = int(os.getenv("MEF_HTTP_TIMEOUT", "300"))


settings = Settings()
