import pytest
from chispa import assert_df_equality
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

from src.transformations.common import clean_ghost_nulls

def test_clean_ghost_nulls(spark):
    """
    Valida que los valores falsos nulos se conviertan a NULL 
    y que se aplique upper() a las columnas que terminan en '_NOMBRE'.
    """
    # 1. Arrange: Datos de entrada con strings sucios
    input_schema = StructType([
        StructField("ID", IntegerType(), True),
        StructField("TIPO", StringType(), True),
        StructField("AREA_NOMBRE", StringType(), True),
    ])
    
    input_data = [
        (1, "Valid", " finanzas "),
        (2, "None", "N/A"),
        (3, "null", "NULL"),
        (4, " ", "  "),
        (5, "-", "--"),
    ]
    
    df_input = spark.createDataFrame(input_data, schema=input_schema)
    
    # 2. Act: Aplicar función a testear
    df_result = clean_ghost_nulls(df_input)
    
    # 3. Assert: Datos esperados
    expected_data = [
        (1, "Valid", "FINANZAS"),  # Se aplicó trim() a TIPO y trim()+upper() a AREA_NOMBRE
        (2, None, None),           # "None" y "N/A" se limpian
        (3, None, None),           # "null" y "NULL" se limpian
        (4, None, None),           # " " y "  " se limpian
        (5, None, None),           # "-" y "--" se limpian
    ]
    
    df_expected = spark.createDataFrame(expected_data, schema=input_schema)
    
    # Comparamos DataFrames usando la librería chispa (muy superior a assertions manuales)
    assert_df_equality(df_result, df_expected, ignore_nullable=True)
