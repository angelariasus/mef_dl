"""
Utilidades de Spark para el proyecto MEF DW v2.
Provee una SparkSession preconfigurada para modo local.
"""
from pyspark.sql import SparkSession


def get_spark(app_name: str = "MEF_Pipeline_v2", memory: str = "4g") -> SparkSession:
    """
    Crea (o reutiliza) una SparkSession optimizada para ejecución local.

    Args:
        app_name: Nombre de la aplicación visible en Spark UI.
        memory:   Memoria para el driver (ej. '4g', '8g').

    Returns:
        SparkSession activa.
    """
    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.driver.memory", memory)
        .config("spark.executor.memory", memory)
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.sql.parquet.compression.codec", "snappy")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.sql.sources.partitionOverwriteMode", "dynamic")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    print(f"[OK] SparkSession lista | version={spark.version} | master={spark.sparkContext.master}")
    return spark


def write_parquet(df, path: str, mode: str = "overwrite", partition_by: list = None) -> int:
    """
    Escribe un DataFrame como Parquet y devuelve el número de filas escritas.

    Args:
        df:           Spark DataFrame a escribir.
        path:         Ruta destino (string con barras forward).
        mode:         'overwrite' | 'append'.
        partition_by: Lista de columnas para particionar.

    Returns:
        Número de filas escritas.
    """
    n = df.count()
    writer = df.write.mode(mode).format("parquet")
    if partition_by:
        writer = writer.partitionBy(*partition_by)
    writer.save(path)
    print(f"  ✅ {n:,} filas → {path}")
    return n


def read_parquet(spark: SparkSession, path: str):
    """Lee un directorio Parquet y lo devuelve como DataFrame."""
    return spark.read.parquet(path)
