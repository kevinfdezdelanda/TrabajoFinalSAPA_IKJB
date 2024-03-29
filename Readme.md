# Proyecto final Sapa Miar Pria

## Descripción

Aplicación Web de Chatbot con Procesamiento de Voz, Generación de Imágenes y Sistema de Acceso mediante Identificación Facial

## Características

- **Procesamiento de Voz:** Permite a los usuarios interactuar con el chatbot usando comandos de voz.
- **Generación de Imágenes basada en Texto:** Capacidad de crear imágenes a partir de descripciones textuales.
- **Sistema de Acceso con Identificación Facial:** Autentica a los usuarios mediante tecnología de reconocimiento facial.

## Tecnologías Utilizadas

- Python
- JavaScript, Html5, Css3
- TensorFlow, Keras
- Flask

## Instalación y Configuración

Proporciona instrucciones detalladas sobre cómo instalar y configurar el proyecto en un entorno local. Incluye los pasos para instalar las dependencias, configurar bases de datos, etc.

Para clonar el repositorio:

```bash
git clone https://github.com/kevinfdezdelanda/TrabajoFinalSAPA_IKJB.git
cd .\TrabajoFinalSAPA_IKJB
```

Para instalar dependencias mediante fichero de requerimientos:

```bash
pip install -r guiribot/requirements.txt
```

Instalación de dependencias de manera manual:

```bash
pip install flask
pip install opencv_python
pip install matplotlib 
pip install mtcnn
pip install tensorflow
pip install transformers
pip install torch torchaudio
pip install datasets
pip install pytest Flask-Testing
pip install soundfile
pip install SentencePiece
pip install click
pip install numpy
pip install pydub
pip install Pillow
pip install Werkzeug
pip install diffusers
```

## Ejecucion en local


```bash
flask --app guiribot run --debug
```

## Inicializar BBDD

```bash
flask --app guiribot init-db
```

## Inicializar pytest

```bash
python -m pytest
```
