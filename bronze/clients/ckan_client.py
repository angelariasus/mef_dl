import time
from typing import Any, Dict, Generator, Tuple
import requests
from bs4 import BeautifulSoup
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
from core.audit.logger import setup_logger
from core.config.settings import settings

logger = setup_logger("mef_dw.clients.ckan_client")
_SEARCH_ENDPOINT = "datastore_search"

class CKANClient:
    """Cliente para interactuar con la API CKAN."""
    BASE_URL = settings.API_BASE_URL.rstrip("/")

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

    @retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=settings.BACKOFF_FACTOR, min=2, max=60),
        retry=retry_if_exception_type(requests.RequestException),
        reraise=True,
    )
    def _get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        t0 = time.time()
        resp = self.session.get(url, params=params, timeout=settings.HTTP_TIMEOUT)
        elapsed = round(time.time() - t0, 2)
        resp.raise_for_status()
        logger.info(f"GET {resp.url} -> {resp.status_code} ({elapsed}s)")
        return resp.json()

    def get_remote_resource_date(self, resource_id: str, page_url: str) -> str:
        """Hace scraping para obtener la fecha de actualización del dataset."""
        if not page_url:
            return "unknown"
        try:
            resp = requests.get(page_url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for row in soup.find_all("tr"):
                th = row.find("th")
                td = row.find("td")
                if th and td and "ltima actualizaci" in th.get_text():
                    date_str = td.get_text().strip()
                    if date_str:
                        return date_str
        except Exception as exc:
            logger.warning(f"Scraping fallido para {page_url}: {exc}")
        return "unknown"

    def iter_pages(self, resource_id: str) -> Generator[Tuple[list, int], None, None]:
        """Extrae la metadata paginada."""
        offset = 0
        while True:
            result = self._get(
                _SEARCH_ENDPOINT,
                params={
                    "resource_id": resource_id,
                    "limit": settings.BATCH_SIZE,
                    "offset": offset,
                    "include_total": "true",
                },
            )
            # Compatibilidad: CKAN estándar vs MEF Custom API
            if "records" in result:
                # MEF Custom API
                records = result.get("records") or []
                inner = result.get("result", {})
                total = int(inner.get("include_total", inner.get("total", 0)))
            else:
                # CKAN Estándar
                inner = result.get("result", {})
                records = inner.get("records") or []
                total = int(inner.get("total", 0))

            if not records:
                break

            yield records, total
            offset += len(records)

            if offset >= total:
                break

            time.sleep(0.3)
