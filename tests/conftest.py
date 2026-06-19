import pytest
from pyspark.sql import SparkSession
import sys
from pathlib import Path

# Agregar src al path para que pytest encuentre los modulos
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

@pytest.fixture(scope="session")
def spark():
    """
    Fixture de nivel de sesión que inicializa una SparkSession en modo local.
    Se ejecuta una sola vez para toda la suite de pruebas, haciendo los tests más rápidos.
    """
    spark_session = (
        SparkSession.builder
        .master("local[1]")
        .appName("pytest-pyspark-local-testing")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    
    yield spark_session
    
    spark_session.stop()
