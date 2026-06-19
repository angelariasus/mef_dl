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
        self.session.headers.update({"User-Agent": "MEF-DW/2.0"})

    def get_remote_file_state(self, url: str) -> str:
        """Obtiene el Last-Modified del ZIP si está disponible."""
        try:
            resp = self.session.head(url, timeout=10)
            return resp.headers.get("Last-Modified", "unknown")
        except Exception as exc:
            logger.warning(f"No se pudo obtener Last-Modified para {url}: {exc}")
            return "unknown"

    def iter_pages(self, url: str, batch_size: int = None, delimiter: str = ',') -> Generator[Tuple[list, int], None, None]:
        """Descarga un ZIP en memoria, busca el primer CSV, y lo emite en lotes JSON."""
        if batch_size is None:
            batch_size = settings.BATCH_SIZE

        t0 = time.time()
        logger.info(f"Descargando ZIP en memoria: {url}")
        
        resp = self.session.get(url, timeout=settings.HTTP_TIMEOUT)
        resp.raise_for_status()
        
        # Leer ZIP en memoria
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            # Buscar el primer archivo CSV dentro del ZIP
            csv_filename = next((f for f in z.namelist() if f.lower().endswith('.csv')), None)
            if not csv_filename:
                raise FileNotFoundError("No se encontró ningún archivo CSV dentro del ZIP.")
            
            logger.info(f"Extrayendo CSV en memoria: {csv_filename}")
            with z.open(csv_filename) as f:
                # El CSV de RENAMU suele tener codificación particular, intentamos latin1
                text_stream = io.TextIOWrapper(f, encoding='latin1', errors='replace')
                reader = csv.DictReader(text_stream, delimiter=delimiter)
                
                batch = []
                total_read = 0
                
                for row in reader:
                    batch.append(row)
                    total_read += 1
                    
                    if len(batch) >= batch_size:
                        yield batch, total_read
                        batch = []
                        
                if batch:
                    yield batch, total_read
                    
        logger.info(f"ZIP procesado ({total_read} filas) en {time.time() - t0:.1f}s")
