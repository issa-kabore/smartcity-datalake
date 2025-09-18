import logging
import sys

# Configure logging for the project
# This setup ensures logs are written to both a file and the console.

# --- Versioning ---
__major__ = 0
__minor__ = 1
__release__ = 1
__pre_release__ = ""
__version__ = f"{__major__}.{__minor__}.{__release__}{__pre_release__}"
__author__ = "Issa KAB"

# --- Logging Configuration ---
# Create a custom logger for this module
# The name of the logger is based on the module's name (__name__)
logger = logging.getLogger(__name__)

# Set the logging level (e.g., INFO, DEBUG, WARNING, ERROR)
logger.setLevel(logging.INFO)

# Create a console handler to print logs to the standard output
console_handler = logging.StreamHandler(sys.stdout)

log_format = "%(asctime)s [%(levelname)s] %(name)s - %(funcName)s - %(message)s"
formatter = logging.Formatter(log_format)

# Set the formatter for the console handler
console_handler.setFormatter(formatter)

# Add the handler to the logger
# This makes sure the logger knows where to send the log messages
if not logger.handlers:
    logger.addHandler(console_handler)

# Do not propagate logs to parent loggers (optional, but good practice)
logger.propagate = False
