from __future__ import annotations
import sys
import time
import json
import itertools
from typing import Any, Dict, List, Tuple

from core.audit.logger import setup_logger
from core.audit.control_manager import ControlManager
from core.storage.storage_manager import storage

from bronze.config import SOURCES
from bronze.models.sources import ApiSource, CsvSource, ZipSource
from bronze.clients.ckan_client import CKANClient
from bronze.clients.csv_client import CsvClient
from bronze.clients.zip_client import ZipClient

logger = setup_logger("mef_dw.ingest_bronze")
QUALITY_SAMPLE_SIZE = 1000

def _has_any_value(record: Dict[str, Any]) -> bool:
    return any(v is not None and v != "" for v in record.values())

def _sample_first_page(generator, arity=2):
    """Extrae la primera página del generador para quality check.
    arity=2 para (batch, total), arity=3 para (batch, total, filename).
    """
    try:
        first = next(generator)
    except StopIteration:
        return [], iter([])
    sample = first[0][:QUALITY_SAMPLE_SIZE]
    full_gen = itertools.chain([first], generator)
    return sample, full_gen

def _should_skip(name: str, folder: str, remote_state: str, state: Dict[str, Any]) -> bool:
    stored = state.get(name, {}).get("remote_state")
    
    if stored is None:
        return False
        
    state_matches = (
        stored == "__legacy__"
        or (remote_state != "unknown" and remote_state == stored)
    )
    
    if not state_matches:
        return False
        
    prefix = f"bronze/{folder}/" if storage.mode == "s3" else f"bronze/{folder}"
    existing = storage.list_paths(prefix, suffix=".json")
    if not existing:
        logger.info(f"Estado coincide pero falta JSON, re-descargando {name}")
        return False
        
    return True

def upload_to_bronze(page_generator, name: str, folder: str) -> Tuple[str, int]:
    """Sube lotes de registros al almacenamiento Bronze (tuplas de 2: batch, total)."""
    total_records = 0
    batch_num = 0

    for records, total in page_generator:
        key = f"bronze/{folder}/batch_{batch_num:05d}.json"
        ndjson_lines = [json.dumps(r, ensure_ascii=False) for r in records]
        data = ("\n".join(ndjson_lines) + "\n").encode("utf-8")
        storage.put_batch(
            key=key,
            data=data,
            metadata={"source": name, "batch": str(batch_num)},
        )
        total_records += len(records)
        batch_num += 1
        pct = round(total_records / total * 100, 1) if total > 0 else "?"
        logger.info(f"  {name} | Lote {batch_num:05d} | {total_records:,}/{total:,} ({pct}%)")

    return f"bronze/{folder}/", total_records


def upload_zip_to_bronze(page_generator, name: str, folder: str) -> Tuple[str, int]:
    """
    Sube lotes provenientes de un ZIP al almacenamiento Bronze.
    Recibe tuplas de 3: (batch, total, csv_filename).
    Inyecta '_source_file' en cada registro para trazabilidad de módulo.
    """
    total_records = 0
    batch_num = 0

    for records, total, csv_filename in page_generator:
        # Normalizar el nombre del archivo (quitar rutas de carpeta, quedarse solo con nombre base)
        import os
        source_tag = os.path.splitext(os.path.basename(csv_filename))[0]

        # Inyectar columna de trazabilidad
        enriched = [{**r, "_source_file": source_tag} for r in records]

        key = f"bronze/{folder}/batch_{batch_num:05d}.json"
        ndjson_lines = [json.dumps(r, ensure_ascii=False) for r in enriched]
        data = ("\n".join(ndjson_lines) + "\n").encode("utf-8")
        storage.put_batch(
            key=key,
            data=data,
            metadata={"source": name, "batch": str(batch_num), "csv_file": source_tag},
        )
        total_records += len(enriched)
        batch_num += 1
        pct = round(total_records / total * 100, 1) if total > 0 else "?"
        logger.info(f"  {name} | [{source_tag}] Lote {batch_num:05d} | {total_records:,}/{total:,} ({pct}%)")

    return f"bronze/{folder}/", total_records

def ingest_api_source(
    source: ApiSource,
    client: CKANClient,
    control: ControlManager,
    state: Dict[str, Any]
) -> Tuple[Dict[str, Any], str]:
    t0 = time.time()
    name = source.name
    try:
        remote_state = client.get_remote_resource_date(source.resource_id, page_url=source.page_url)
        
        if _should_skip(name, source.folder, remote_state, state):
            logger.info(f"Fuente {name} sin cambios ({remote_state}), omitiendo.")
            return {"status": "skipped", "name": name}, remote_state

        generator = client.iter_pages(source.resource_id)
        sample, generator = _sample_first_page(generator)
        
        # Quality check on-the-fly
        failed_count = sum(1 for row in sample if not _has_any_value(row))
        control.log_quality_check(
            check_name=f"completeness_{name}",
            dataset=name,
            records_checked=len(sample),
            records_failed=failed_count
        )
        
        s3_path, total = upload_to_bronze(generator, name, source.folder)
        elapsed = round(time.time() - t0, 1)
        
        logger.info(f"Fuente API extraída: {name} | {total} filas | {elapsed}s")
        return {"status": "success", "name": name, "rows": total, "s3_path": s3_path, "ms": elapsed}, remote_state
        
    except Exception as exc:
        control.log_error(
            error_type="APIIngestionError",
            message=str(exc),
            context={"name": name, "resource_id": source.resource_id},
        )
        logger.error(f"Error en fuente API {name}: {exc}")
        return {"status": "error", "name": name, "error": str(exc)}, "unknown"

def ingest_csv_source(
    source: CsvSource,
    client: CsvClient,
    control: ControlManager,
    state: Dict[str, Any]
) -> Tuple[Dict[str, Any], str]:
    t0 = time.time()
    name = source.name
    try:
        remote_state = client.get_remote_file_state(source.url)
        
        if _should_skip(name, source.folder, remote_state, state):
            logger.info(f"Fuente {name} sin cambios ({remote_state}), omitiendo.")
            return {"status": "skipped", "name": name}, remote_state

        generator = client.iter_pages(source.url)
        sample, generator = _sample_first_page(generator)
        
        failed_count = sum(1 for row in sample if not _has_any_value(row))
        control.log_quality_check(
            check_name=f"completeness_{name}",
            dataset=name,
            records_checked=len(sample),
            records_failed=failed_count
        )
        
        s3_path, total = upload_to_bronze(generator, name, source.folder)
        elapsed = round(time.time() - t0, 1)
        
        logger.info(f"Fuente CSV extraída: {name} | {total} filas | {elapsed}s")
        return {"status": "success", "name": name, "rows": total, "s3_path": s3_path, "ms": elapsed}, remote_state
        
    except Exception as exc:
        control.log_error("CSVIngestionError", str(exc), {"name": name, "url": source.url})
        logger.error(f"Error en fuente CSV {name}: {exc}")
        return {"status": "error", "name": name, "error": str(exc)}, "unknown"


def ingest_zip_source(
    source: ZipSource,
    client: ZipClient,
    control: ControlManager,
    state: Dict[str, Any]
) -> Tuple[Dict[str, Any], str]:
    t0 = time.time()
    name = source.name
    try:
        remote_state = client.get_remote_file_state(source.url)
        
        if _should_skip(name, source.folder, remote_state, state):
            logger.info(f"Fuente {name} sin cambios ({remote_state}), omitiendo.")
            return {"status": "skipped", "name": name}, remote_state

        generator = client.iter_pages(source.url, delimiter=source.delimiter)
        sample, generator = _sample_first_page(generator, arity=3)

        failed_count = sum(1 for row in sample if not _has_any_value(row))
        control.log_quality_check(
            check_name=f"completeness_{name}",
            dataset=name,
            records_checked=len(sample),
            records_failed=failed_count
        )

        s3_path, total = upload_zip_to_bronze(generator, name, source.folder)
        elapsed = round(time.time() - t0, 1)
        
        logger.info(f"Fuente ZIP extraída: {name} | {total} filas | {elapsed}s")
        return {"status": "success", "name": name, "rows": total, "s3_path": s3_path, "ms": elapsed}, remote_state
        
    except Exception as exc:
        control.log_error("ZIPIngestionError", str(exc), {"name": name, "url": source.url})
        logger.error(f"Error en fuente ZIP {name}: {exc}")
        return {"status": "error", "name": name, "error": str(exc)}, "unknown"


def run_pipeline(source_prefix: str = None, year_filter: str = None) -> Dict[str, Any]:
    ckan_client = CKANClient()
    csv_client = CsvClient()
    zip_client = ZipClient()
    
    # Audit Control setup
    from core.audit.control_manager import ExecutionStatus, ControlManager

    control = ControlManager(pipeline_name="bronze_mef")

    filtered_sources = []
    for s in SOURCES:
        if source_prefix and not s.folder.startswith(source_prefix.lower()):
            continue
        if year_filter and year_filter not in s.name and year_filter not in s.folder:
            continue
        filtered_sources.append(s)

    source_names = [s.name for s in filtered_sources]
    execution = control.start(input_parameters={"sources": source_names})

    logger.info("=" * 60)
    logger.info(f"START - Bronze Pipeline MEF | exec_id={execution.execution_id}")
    logger.info("=" * 60)

    state = storage.read_state()
    results = []

    for source in filtered_sources:
        logger.info(f"[{source.name}] Procesando...")
        if isinstance(source, ApiSource):
            result, remote_state = ingest_api_source(source, ckan_client, control, state)
        elif isinstance(source, CsvSource):
            result, remote_state = ingest_csv_source(source, csv_client, control, state)
        elif isinstance(source, ZipSource):
            result, remote_state = ingest_zip_source(source, zip_client, control, state)
        else:
            result = {"status": "skipped", "name": source.name}
            remote_state = "unknown"
            
        results.append(result)
        
        if result["status"] in ("success", "skipped"):
            # Si remote_state es unknown pero se procesó con éxito (o se skipeó), guardamos "__legacy__" 
            # para poder skipearlo en adelante si el local existe
            resolved_state = remote_state if remote_state != "unknown" else "__legacy__"
            state = storage.read_state()
            state[source.name] = {"remote_state": resolved_state}
            storage.write_state(state)

    successful = sum(1 for r in results if r["status"] == "success")
    skipped    = sum(1 for r in results if r["status"] == "skipped")
    errors     = [r for r in results if r["status"] == "error"]

    if successful + skipped == len(results):
        final_status = ExecutionStatus.SUCCESS
    elif successful == 0 and skipped == 0:
        final_status = ExecutionStatus.FAILED
    else:
        final_status = ExecutionStatus.PARTIAL

    output_summary = {
        "total_sources": len(results),
        "successful": successful,
        "skipped": skipped,
        "failed": len(errors),
        "errors": errors,
        "source_details": results
    }

    control.end(status=final_status, output_summary=output_summary)
    
    logger.info("=" * 60)
    logger.info(f"END - Bronze Pipeline MEF | OK={successful} SKIP={skipped} ERR={len(errors)}")
    logger.info("=" * 60)
    return output_summary

def run(years=None, force=False, source_group=None):
    # Compatibilidad para el DAG existente
    run_pipeline(source_prefix=source_group)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingesta de la Capa Bronze del MEF")
    parser.add_argument("--source", type=str, help="Filtra por grupo de fuente (ej. siaf, sismepre, renamu)")
    parser.add_argument("--year", type=str, help="Filtra por año específico (ej. 2024)")
    args = parser.parse_args()

    res = run_pipeline(source_prefix=args.source, year_filter=args.year)
    if res["failed"] > 0:
        sys.exit(1)
