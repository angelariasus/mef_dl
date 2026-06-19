from dataclasses import dataclass

@dataclass
class DataSource:
    name: str
    folder: str
    type: str

@dataclass
class ApiSource(DataSource):
    resource_id: str
    page_url: str

@dataclass
class CsvSource(DataSource):
    url: str

@dataclass
class ZipSource(DataSource):
    url: str
    delimiter: str = ","
