"""
Transformaciones comunes reutilizables en todas las capas Silver.
Estas funciones se importan desde los notebooks para mantenerlos legibles.
"""
from typing import List, Dict, Any
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

# Valores que se consideran nulos "falsos" (ghost nulls)
GHOST_NULLS: List[str] = [
    "", " ", "None", "none", "nan", "NaN", "NULL", "null",
    "N/A", "n/a", "--", "-",
]


def clean_ghost_nulls(df: DataFrame) -> DataFrame:
    """
    Reemplaza todos los valores ghost-null por NULL real en columnas string.
    También aplica trim() y upper() a columnas que terminan en '_NOMBRE'.
    """
    str_cols = [f.name for f in df.schema.fields if f.dataType == StringType()]
    exprs = []
    for c in df.columns:
        if c in str_cols:
            expr = F.when(
                F.trim(F.col(c)).isin(GHOST_NULLS),
                F.lit(None)
            ).otherwise(F.trim(F.col(c)))
            if c.endswith("_NOMBRE") or c.endswith("_DESC"):
                expr = F.upper(expr)
            exprs.append(expr.alias(c))
        else:
            exprs.append(F.col(c))
    return df.select(*exprs)


def print_dq_summary(df: DataFrame, dq_cols: List[str]) -> None:
    """
    Imprime un resumen de los DQ Flags: cuántos registros fallan cada flag.
    """
    print("\n📊 Resumen de Quality Flags:")
    print(f"  {'Flag':<30} {'Registros con flag':>20}")
    print("  " + "-" * 52)
    for col in dq_cols:
        if col in df.columns:
            count = df.filter(F.col(col) == 1).count()
            total = df.count()
            pct = (count / total * 100) if total > 0 else 0
            print(f"  {col:<30} {count:>10,}  ({pct:.1f}%)")
