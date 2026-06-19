import csv
import time
from typing import Dict, Any, Generator, Tuple
import requests

from core.audit.logger import setup_logger
from core.config.settings import settings

logger = setup_logger("mef_dw.clients.csv_client")

class CsvClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "MEF-DL/2.0"})

    def get_remote_file_state(self, url: str) -> str:
        """Obtiene el Last-Modified del CSV si está disponible."""
        try:
            resp = self.session.head(url, timeout=10)
            return resp.headers.get("Last-Modified", "unknown")
        except Exception as exc:
            logger.warning(f"No se pudo obtener Last-Modified para {url}: {exc}")
            return "unknown"

    def iter_pages(self, url: str, batch_size: int = None) -> Generator[Tuple[list, int], None, None]:
        """Descarga el CSV en streaming y lo emite en lotes (como JSON)."""
        if batch_size is None:
            batch_size = settings.BATCH_SIZE

        t0 = time.time()
        logger.info(f"Descargando CSV: {url}")
        
        with self.session.get(url, stream=True, timeout=settings.HTTP_TIMEOUT) as resp:
            resp.raise_for_status()
            
            # Asumimos utf-8 para el CSV
            lines = (line.decode('utf-8', errors='replace') for line in resp.iter_lines())
            reader = csv.DictReader(lines)
            
            batch = []
            total_read = 0
            
            for row in reader:
                batch.append(row)
                total_read += 1
                
                if len(batch) >= batch_size:
                    # El total no lo sabemos hasta terminar, pasamos 0 o el total acumulado
                    yield batch, total_read
                    batch = []
                    
            if batch:
                yield batch, total_read
                
        logger.info(f"CSV procesado ({total_read} filas) en {time.time() - t0:.1f}s")
