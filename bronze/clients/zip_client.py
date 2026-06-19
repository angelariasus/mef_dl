import csv
import io
import time
import zipfile
from typing import Dict, Any, Generator, Tuple
import requests

from core.audit.logger import setup_logger
from core.config.settings import settings

logger = setup_logger("mef_dw.clients.zip_client")

class ZipClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "MEF-DL/2.0"})

    def get_remote_file_state(self, url: str) -> str:
        """Obtiene el Last-Modified del ZIP si está disponible."""
        try:
            resp = self.session.head(url, timeout=10)
            return resp.headers.get("Last-Modified", "unknown")
        except Exception as exc:
            logger.warning(f"No se pudo obtener Last-Modified para {url}: {exc}")
            return "unknown"

    def iter_pages(self, url: str, batch_size: int = None, delimiter: str = ',') -> Generator[Tuple[list, int, str], None, None]:
        """
        Descarga un ZIP en memoria e itera sobre TODOS los archivos CSV que contiene,
        emitiendo lotes con el nombre del archivo de origen incluido.

        Para ZIPs con un único CSV (ej. SIAF histórico, RENAMU 2021+), emite ese archivo.
        Para ZIPs con múltiples módulos/carpetas (ej. RENAMU 2012-2020), emite cada CSV
        por separado, permitiendo trazabilidad del módulo de origen.

        Yields:
            (batch: list[dict], total_read: int, source_filename: str)
        """
        if batch_size is None:
            batch_size = settings.BATCH_SIZE

        t0 = time.time()
        logger.info(f"Descargando ZIP en memoria: {url}")

        resp = self.session.get(url, timeout=settings.HTTP_TIMEOUT)
        resp.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            # Listar todos los CSVs dentro del ZIP (ignora PDFs, etc.)
            csv_files = sorted(f for f in z.namelist() if f.lower().endswith('.csv'))

            if not csv_files:
                raise FileNotFoundError("No se encontró ningún archivo CSV dentro del ZIP.")

            logger.info(f"ZIP contiene {len(csv_files)} archivo(s) CSV.")

            for csv_filename in csv_files:
                logger.info(f"Procesando: {csv_filename}")
                try:
                    with z.open(csv_filename) as f:
                        text_stream = io.TextIOWrapper(f, encoding='latin1', errors='replace')
                        reader = csv.DictReader(text_stream, delimiter=delimiter)

                        batch = []
                        total_read = 0

                        for row in reader:
                            batch.append(row)
                            total_read += 1

                            if len(batch) >= batch_size:
                                yield batch, total_read, csv_filename
                                batch = []

                        if batch:
                            yield batch, total_read, csv_filename

                    logger.info(f"  -> {csv_filename}: {total_read} filas")
                except Exception as exc:
                    logger.warning(f"  -> No se pudo leer {csv_filename}: {exc}. Omitiendo.")
                    continue

        logger.info(f"ZIP procesado completamente en {time.time() - t0:.1f}s")

