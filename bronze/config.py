from typing import List
from bronze.models.sources import DataSource, ApiSource, CsvSource, ZipSource
from core.config.settings import settings

SOURCES: List[DataSource] = []

# 1. SIAF
for year in settings.YEARS:
    zip_url = getattr(settings, "SIAF_ZIP_URLS", {}).get(year)
    if zip_url:
        SOURCES.append(
            ZipSource(
                name=f"SIAF_{year}",
                folder=f"siaf/{year}",
                type="zip",
                url=zip_url,
                delimiter=","
            )
        )
    else:
        resource_id = settings.RESOURCE_IDS.get(year)
        page_url = settings.PAGE_URLS.get(year)
        
        if resource_id and page_url:
            SOURCES.append(
                ApiSource(
                    name=f"SIAF_{year}",
                    folder=f"siaf/{year}",
                    type="api",
                    resource_id=resource_id,
                    page_url=page_url
                )
            )

# 2. SISMEPRE
for name, resource_id in getattr(settings, "SISMEPRE_RESOURCE_IDS", {}).items():
    page_url = getattr(settings, "SISMEPRE_PAGE_URLS", {}).get(name)
    if resource_id and page_url:
        SOURCES.append(
            ApiSource(
                name=name,
                folder=f"sismepre/{name.lower()}",
                type="api",
                resource_id=resource_id,
                page_url=page_url
            )
        )

# 3. RENAMU
for year, zip_url in getattr(settings, "RENAMU_ZIP_URLS", {}).items():
    if zip_url:
        SOURCES.append(
            ZipSource(
                name=f"RENAMU_{year}",
                folder=f"renamu/{year}",
                type="zip",
                url=zip_url,
                delimiter=";"
            )
        )
