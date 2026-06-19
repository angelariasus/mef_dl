"""
Storage Manager — Capa de Abstracción Local.

Centraliza:
  - Lectura y escritura de archivos de estado (state.json) incremental.
  - Escritura de lotes JSON de Bronze.
  - Verificación de existencia de archivos.
  - Resolución de rutas para que Spark y Polars las consuman.

Uso:
    from core.storage.storage_manager import storage
    storage.write_state(state_dict)
    state = storage.read_state()
    storage.put_batch("bronze/2024/batch_00001.json", json_bytes)
    paths = storage.list_paths("bronze/2024/", suffix=".json")
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.audit.logger import setup_logger
from core.config.settings import settings

logger = setup_logger("mef_dw.storage.storage_manager")


class StorageManager:
    """
    Gestor de almacenamiento local.

    Instanciar directamente no es necesario; usar el singleton `storage`.
    """

    def __init__(self):
        self.mode = "local"
        logger.info("StorageManager iniciado en modo LOCAL")

    # ── Resolución de Rutas ───────────────────────────────────────────────────

    def bronze_path(self, year: Optional[int] = None) -> str:
        """Devuelve la ruta raíz de Bronze (o de un año específico)."""
        base = settings.BRONZE_DIR
        return str(base / str(year)) if year else str(base)

    def silver_path(self) -> str:
        """Devuelve la ruta raíz de Silver."""
        return str(settings.SILVER_DIR).replace("\\", "/")

    def gold_path(self, sub: str = "") -> str:
        """Devuelve la ruta a la capa Gold, o un subdirectorio si se provee."""
        base = settings.GOLD_DIR / sub if sub else settings.GOLD_DIR
        return str(base).replace("\\", "/")

    def audit_path(self, sub: str = "") -> str:
        """Devuelve la ruta de la carpeta de auditoría."""
        local = settings.PROJECT_ROOT / "data" / "audit" / sub
        local.mkdir(parents=True, exist_ok=True)
        return str(local)

    def state_key(self) -> str:
        """Clave/ruta del archivo de estado incremental."""
        return str(settings.STATE_FILE)

    # ── Operaciones de Estado Incremental ────────────────────────────────────

    def read_state(self) -> Dict[str, Any]:
        """Lee el estado incremental (JSON) desde disco."""
        state_file = Path(self.state_key())
        if not state_file.exists():
            logger.info("Sin archivo de estado local — primera ejecución.")
            return {}
        state = json.loads(state_file.read_text(encoding="utf-8"))
        logger.info(f"Estado leído desde disco: {state_file}")
        return state

    def write_state(self, state: Dict[str, Any]) -> None:
        """Persiste el estado incremental (JSON) en disco."""
        state["_last_updated"] = datetime.utcnow().isoformat() + "Z"
        content = json.dumps(state, ensure_ascii=False, indent=2).encode("utf-8")
        state_file = Path(self.state_key())
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_bytes(content)
        logger.info(f"Estado guardado localmente: {state_file}")

    # ── Escritura de Objetos (Lotes JSON Bronze) ──────────────────────────────

    def put_batch(self, key: str, data: bytes, metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Escribe un lote de datos en disco local.

        Args:
            key:      Clave relativa (ej. "bronze/2024/batch_00001.json").
            data:     Bytes del contenido.
            metadata: Ignorado en almacenamiento local.

        Returns:
            Ruta local completa.
        """
        local = settings.PROJECT_ROOT / "data" / key
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(data)
        logger.debug(f"Lote guardado localmente: {local}")
        return str(local)

    # ── Listado de Objetos ────────────────────────────────────────────────────

    def list_paths(self, prefix: str, suffix: str = ".json") -> List[str]:
        """
        Lista objetos bajo un prefijo, filtrados por sufijo.
        Devuelve rutas locales completas.
        """
        base = settings.PROJECT_ROOT / "data" / prefix
        if not base.exists():
            return []
        return sorted(str(p) for p in base.rglob(f"*{suffix}"))

    def get_latest_parquet(self, prefix: str) -> Optional[str]:
        """
        Retorna la ruta del archivo Parquet más reciente bajo un prefijo.
        Asume que los nombres de archivo contienen sufijos ordenables (ej. timestamps o fechas).
        """
        paths = self.list_paths(prefix, suffix=".parquet")
        if not paths:
            return None
        return paths[-1]

    # ── Verificación de Existencia ────────────────────────────────────────────

    def exists(self, key: str) -> bool:
        """Verifica si un archivo local existe."""
        local = settings.PROJECT_ROOT / "data" / key
        return local.exists()

    # ── Upload de Reportes JSON ───────────────────────────────────────────────

    def save_report(self, report: Dict[str, Any], relative_key: str) -> str:
        """Guarda un reporte JSON en disco."""
        content = json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")
        local = settings.PROJECT_ROOT / "data" / relative_key
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(content)
        logger.info(f"Reporte guardado localmente: {local}")
        return str(local)


# ── Singleton global ──────────────────────────────────────────────────────────
storage = StorageManager()
