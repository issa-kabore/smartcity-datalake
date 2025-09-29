import os
import logging
from prefect.logging import get_run_logger

_LOGGER_INITIALIZED = False

def _configure_base_logger(name="smartcity"):
    global _LOGGER_INITIALIZED
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers and not _LOGGER_INITIALIZED:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(funcName)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        _LOGGER_INITIALIZED = True
    logger.propagate = False
    return logger

def get_smartcity_logger(name="smartcity") -> logging.Logger:
    env = os.getenv("ENV", "local")
    if env == "prod" or os.getenv("PREFECT__FLOW_RUN_ID"):
        return get_run_logger()  # type: ignore
    return _configure_base_logger(name)
