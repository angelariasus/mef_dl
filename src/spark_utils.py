"""
Utilidades de Spark para el proyecto MEF DL v2.
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


def write_parquet(
    df,
    path: str,
    mode: str = "overwrite",
    partition_by: list = None,
    coalesce_to: int = None,
) -> int:
    """
    Escribe un DataFrame como Parquet y devuelve el número de filas escritas.

    Args:
        df:           Spark DataFrame a escribir.
        path:         Ruta destino (string con barras forward).
        mode:         'overwrite' | 'append'.
        partition_by: Lista de columnas para particionar. Cuando se usa junto
                      con coalesce_to, el coalesce se aplica por partición
                      (Spark distribuye internamente).
        coalesce_to:  Número máximo de archivos de salida. Usa coalesce()
                      (sin shuffle) para reducir el small-file problem.
                      Recomendado: 1 para tablas < 128 MB sin particionado,
                      1 para tablas particionadas donde cada partición < 128 MB.

    Returns:
        Número de filas escritas.
    """
    n = df.count()
    # Aplicar coalesce antes de escribir para consolidar archivos pequeños.
    # coalesce() es preferible a repartition() porque evita shuffle completo.
    if coalesce_to is not None:
        df = df.coalesce(coalesce_to)
    writer = df.write.mode(mode).format("parquet")
    if partition_by:
        writer = writer.partitionBy(*partition_by)
    writer.save(path)
    print(f"  ✅ {n:,} filas → {path}")
    return n


def read_parquet(spark: SparkSession, path: str):
    """Lee un directorio Parquet y lo devuelve como DataFrame."""
    return spark.read.parquet(path)
