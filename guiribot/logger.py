import datetime
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger():
    # Crea un logger
    logger = logging.getLogger('guiribot')

    # Establece el nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    logger.setLevel(logging.INFO)

    # Fecha actual
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    # Crear el nombre del archivo con la fecha
    #log_filename = f"logs/{date_str}-guiribot.log"
    log_filename = Path("logs") / f"{date_str}-guiribot.log"
    
    # Crea un handler de archivo que escribe logs con rotación
    handler = RotatingFileHandler(log_filename, maxBytes=10000, backupCount=3)

    # Formato de los logs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Añade el handler al logger
    logger.addHandler(handler)

    return logger

# Configura un logger global
app_logger = setup_logger()