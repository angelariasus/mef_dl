"""
Sistema de Auditoría de Ejecuciones del Pipeline.

Registra el ciclo de vida completo de cada ejecución del pipeline:
  - Hora de inicio y fin
  - Parámetros de entrada
  - Registros procesados / fallidos
  - Resultados de checks de calidad
  - Errores capturados

Los reportes se guardan como JSON en data/audit/executions/.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.audit.logger import setup_logger
from core.config.settings import settings

logger = setup_logger("mef_dw.audit.control_manager")


# ── Enums de Estado ───────────────────────────────────────────────────────────

class ExecutionStatus(str, Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED  = "FAILED"


class QualityStatus(str, Enum):
    PASSED  = "PASSED"
    WARNING = "WARNING"
    FAILED  = "FAILED"


# ── Schemas de Datos ──────────────────────────────────────────────────────────

@dataclass
class QualityCheckResult:
    check_id:        str
    check_name:      str
    dataset:         str
    status:          QualityStatus
    records_checked: int
    records_passed:  int
    records_failed:  int
    failure_rate:    float
    details:         Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id":        self.check_id,
            "check_name":      self.check_name,
            "dataset":         self.dataset,
            "status":          self.status.value,
            "records_checked": self.records_checked,
            "records_passed":  self.records_passed,
            "records_failed":  self.records_failed,
            "failure_rate":    self.failure_rate,
            "details":         self.details,
        }


@dataclass
class ExecutionRecord:
    pipeline_name:    str
    input_parameters: Dict[str, Any]
    execution_id:     str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    start_time:       datetime = field(default_factory=datetime.now)
    end_time:         Optional[datetime] = None
    status:           ExecutionStatus = ExecutionStatus.RUNNING
    output_summary:   Dict[str, Any] = field(default_factory=dict)
    quality_checks:   List[QualityCheckResult] = field(default_factory=list)
    errors:           List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id":     self.execution_id,
            "pipeline_name":    self.pipeline_name,
            "status":           self.status.value,
            "start_time":       self.start_time.isoformat(),
            "end_time":         self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (
                (self.end_time - self.start_time).total_seconds()
                if self.end_time else None
            ),
            "input_parameters": self.input_parameters,
            "output_summary":   self.output_summary,
            "quality_checks":   [qc.to_dict() for qc in self.quality_checks],
            "quality_passed":   sum(1 for qc in self.quality_checks if qc.status == QualityStatus.PASSED),
            "errors":           self.errors,
        }


# ── ControlManager ────────────────────────────────────────────────────────────

class ControlManager:
    """
    Gestiona el ciclo de vida de una ejecución del pipeline.

    Uso típico:
        control = ControlManager("bronze_pipeline")
        execution = control.start({"years": [2022, 2023]})
        ...
        control.end(ExecutionStatus.SUCCESS, {"rows": 500000})
    """

    AUDIT_DIR: Path = settings.PROJECT_ROOT / "data" / "audit" / "executions"

    def __init__(self, pipeline_name: str):
        self.pipeline_name = pipeline_name
        self.execution: Optional[ExecutionRecord] = None

    def start(self, input_parameters: Dict[str, Any]) -> ExecutionRecord:
        """Inicia una nueva ejecución y la registra."""
        self.execution = ExecutionRecord(
            pipeline_name=self.pipeline_name,
            input_parameters=input_parameters,
        )
        logger.info(
            f"[AUDIT] Ejecución iniciada | pipeline={self.pipeline_name} "
            f"id={self.execution.execution_id}"
        )
        return self.execution

    def end(
        self,
        status: ExecutionStatus,
        output_summary: Dict[str, Any],
    ) -> ExecutionRecord:
        """Cierra la ejecución, calcula duración y persiste el reporte."""
        if not self.execution:
            raise RuntimeError("No hay ejecución activa. Llama a start() primero.")

        self.execution.end_time      = datetime.now()
        self.execution.status        = status
        self.execution.output_summary = output_summary

        duration = (self.execution.end_time - self.execution.start_time).total_seconds()
        logger.info(
            f"[AUDIT] Ejecución terminada | id={self.execution.execution_id} "
            f"status={status.value} duration={duration:.1f}s"
        )
        self._save()
        return self.execution

    def log_quality_check(
        self,
        check_name: str,
        dataset: str,
        records_checked: int,
        records_failed: int,
        details: Optional[Dict[str, Any]] = None,
        threshold: float = 0.05,
    ) -> QualityCheckResult:
        """Registra el resultado de un check de calidad."""
        if not self.execution:
            raise RuntimeError("No hay ejecución activa.")

        records_passed = records_checked - records_failed
        failure_rate   = records_failed / records_checked if records_checked > 0 else 0.0

        if failure_rate == 0:
            status = QualityStatus.PASSED
        elif failure_rate < threshold:
            status = QualityStatus.WARNING
        else:
            status = QualityStatus.FAILED

        check = QualityCheckResult(
            check_id=f"{check_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            check_name=check_name,
            dataset=dataset,
            status=status,
            records_checked=records_checked,
            records_passed=records_passed,
            records_failed=records_failed,
            failure_rate=failure_rate,
            details=details or {"threshold": threshold},
        )
        self.execution.quality_checks.append(check)
        logger.info(
            f"[AUDIT] Quality check '{check_name}' | dataset={dataset} "
            f"status={status.value} failure_rate={failure_rate:.4f}"
        )
        return check

    def log_error(self, error_type: str, message: str, context: Dict[str, Any] = None) -> None:
        """Registra un error ocurrido durante la ejecución."""
        if not self.execution:
            return
        entry = {
            "error_type":    error_type,
            "error_message": message,
            "context":       context or {},
            "timestamp":     datetime.now().isoformat(),
        }
        self.execution.errors.append(entry)
        logger.error(f"[AUDIT] Error registrado: {error_type} — {message}")

    def get_report(self) -> Dict[str, Any]:
        """Devuelve el reporte completo de la ejecución actual."""
        if not self.execution:
            return {"error": "Sin ejecución activa"}
        return self.execution.to_dict()

    def _save(self) -> None:
        """Persiste el reporte de ejecución en disco."""
        self.AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.AUDIT_DIR / f"{ts}_{self.execution.execution_id}_{self.pipeline_name}.json"
        report_path.write_text(
            json.dumps(self.execution.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info(f"[AUDIT] Reporte guardado: {report_path}")
