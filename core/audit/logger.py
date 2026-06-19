import logging
import sys
from pathlib import Path


def setup_logger(name: str, log_dir: Path = None) -> logging.Logger:
    """
    Crea un logger con salida a consola y, opcionalmente, a archivo.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Consola
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # Archivo (opcional)
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_dir / f"{name.split('.')[-1]}.log", encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger
