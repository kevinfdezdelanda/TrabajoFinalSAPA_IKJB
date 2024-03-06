#!/usr/bin/python3
import sys
import logging
# import site

"""
app.wsgi
Este fichero WSGI hace de puente entre Apache y la app Flask.
"""

# Añade el directorio de la app al path de Python. Esto es necesario para que el
# intérprete de Python pueda encontrar y cargar la app Flask correctamente.
sys.path.insert(0,"/var/www/html/guiribot/")

# Configura logging básico. Esto asegura que los errores y mensajes de la app
# se escriban en los logs de Apache.
logging.basicConfig(stream=sys.stderr)

# Añade el directorio de paquetes del sitio al sys.path. No es estrictamente necesario
# porque la configuración de Apache ya apunta al módulo correcto en el directorio
# del entorno virtual.
# site.addsitedir("/var/www/entorno_virtual/lib/python3.9/site-packages/")

# Importa la app Flask.
# from app: nombre del fichero Python de la app
# import app: nombre de la variable que contiene la app Flask. app = Flask(__name__)
from guiribot import app as application

