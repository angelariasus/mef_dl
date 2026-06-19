from pathlib import Path
from src.paths import PROJECT_ROOT, DATA_ROOT, BRONZE, SILVER, GOLD

def test_project_root_exists():
    """Valida que la raíz del proyecto exista y sea un directorio."""
    assert PROJECT_ROOT.exists()
    assert PROJECT_ROOT.is_dir()

def test_data_root_is_within_project():
    """Valida que la carpeta data esté dentro del proyecto."""
    assert DATA_ROOT.parent == PROJECT_ROOT
    assert DATA_ROOT.name == "data"

def test_bronze_paths_are_configured():
    """Valida que existan diccionarios de configuración para cada capa."""
    assert isinstance(BRONZE, dict)
    assert "siaf" in BRONZE
    assert "sismepre" in BRONZE
    assert "renamu" in BRONZE

def test_silver_and_gold_paths_configured():
    assert isinstance(SILVER, dict)
    assert isinstance(GOLD, dict)
    assert len(SILVER) >= 3
    assert len(GOLD) >= 3
