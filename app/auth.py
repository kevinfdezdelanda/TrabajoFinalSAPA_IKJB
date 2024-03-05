import functools
from io import BytesIO
import os
import cv2
from matplotlib import pyplot as plt
from mtcnn.mtcnn import MTCNN
import numpy as np
from PIL import Image

from werkzeug.utils import secure_filename

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# CONFIG
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"users_img") # your path

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        img_file = request.files['imagen']
        db = get_db()
        error = None

        if not username:
            error = 'Nombre de usuario requerido'
        elif not img_file:
            error = 'Img requerida'

        if username and existe_usuario(username):
           error = f"Usuario ya registrado"

        if error is None:
            
            try:    
                img_stream = img_file.read()

                # Convertir los datos binarios a un array de NumPy para OpenCV
                np_img = np.frombuffer(img_stream, np.uint8)
                img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                
                # Detecto las caras de las img
                faces = MTCNN().detect_faces(img)
                if (len(faces) == 0):
                    error = "Cara no detectada"
                else:
                    # Voy guardando las caras en su carpeta (users_img)
                    pic = face2(img,faces)
                    
                    # Convertir el numpy array a un objeto de imagen PIL
                    img_pil = Image.fromarray(pic)

                    # Crear un objeto BytesIO para almacenar los datos de la imagen
                    img_byte_arr = BytesIO()

                    # Guardar la imagen en el objeto BytesIO (aquí se usa el formato PNG, pero también puede ser JPEG)
                    img_pil.save(img_byte_arr, format='PNG')

                    # Los datos binarios están ahora en img_byte_arr.getvalue()
                    img_binary_data = img_byte_arr.getvalue()

                    db.execute(
                        "INSERT INTO user (name, photo) VALUES (?, ?)",
                        (username, img_binary_data),
                    )
                    db.commit()
                        
                    return redirect(url_for("auth.login"))


            except db.IntegrityError:
                error = f"Usuario ya registrado"
                
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # Obtengo los datos del formulario de login
        username = request.form['username']
        img_file = request.files['imagen']

        error = None

        if not username:
            error = 'Nombre de usuario requerido'
        elif not img_file:
            error = 'Img requerida'
        print(img_file)
        if error is None:
            img_db, id = obtener_foto_usuario(username)
            
            if img_db is None:
                error = 'Usuario no encontrado'
            else:
                img_stream = img_file.read()

                # Convertir los datos binarios a un array de NumPy para OpenCV
                np_img = np.frombuffer(img_stream, np.uint8)
                img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                
                # Detecto las caras de las img
                faces = MTCNN().detect_faces(img)
                
                if(len(faces) == 0):
                    error = 'Error: Cara no detectada'
                else:
                    # Voy guardando las caras en su carpeta (users_img)
                    img_login = face2(img,faces)
                    
                    print(type(img_login), type(img_db))
                    comp = compatibility(img_login, img_db)
                
                    # Si la compatibilidad es mayor de 0.8 hara el login
                    if comp >= 0.80:
                        session.clear()
                        session['username'] = username
                        return redirect(url_for('index'))
                    else:
                        error = 'Reconocimiento facial fallido'

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    username = session.get('username')

    if username is None:
        g.user = None
    else:
        g.user = username
        
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

def convertToBinaryData(filename):
    # Convert digital data to binary format
    try:
        with open(filename, 'rb') as file:
            binaryData = file.read()
        return binaryData
    except:
        return 0
    
def write_file(data, path):
    # Convert binary data to proper format and write it on your computer
    with open(path, 'wb') as file:
        file.write(data)
        
def face( ruta_img, data, faces):
    for i in range(len(faces)):
        x1, y1, ancho, alto = faces[i]["box"]
        x2, y2 = x1 + ancho, y1 + alto
        # plt.subplot(1,len(faces), i + 1)
        # plt.axis("off")
        face = cv2.resize(data[y1:y2, x1:x2],(150,200), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(ruta_img, face)
        # plt.imshow(data[y1:y2, x1:x2])

# Devuleve la primera cara encontrada
def face2(data, faces):
    for i in range(len(faces)):
        x1, y1, ancho, alto = faces[i]["box"]
        x2, y2 = x1 + ancho, y1 + alto
        # plt.subplot(1,len(faces), i + 1)
        # plt.axis("off")
        face = cv2.resize(data[y1:y2, x1:x2],(150,200), interpolation=cv2.INTER_CUBIC)
        return face
        # plt.imshow(data[y1:y2, x1:x2])
    

def compatibility(img1, img2):
    # Convertir a escala de grises si es necesario
    if len(img1.shape) == 3:
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    if len(img2.shape) == 3:
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    orb = cv2.ORB_create()

    kpa, dac1 = orb.detectAndCompute(img1, None)
    kpb, dac2 = orb.detectAndCompute(img2, None)

    if dac1 is None or dac2 is None:
        return 0

    # Crear BFMatcher con parámetros apropiados
    comp = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # Asegúrate de que hay descriptores para comparar
    if dac1.shape[0] == 0 or dac2.shape[0] == 0:
        return 0

    # Comparar los descriptores
    matches = comp.match(dac1, dac2)

    similar = [x for x in matches if x.distance < 70]
    if len(matches) == 0:
        return 0
    return len(similar) / len(matches)

def obtener_foto_usuario(username):
    # Conectar a la base de datos SQLite
    db = get_db()
    cursor = db.cursor()

    try:
        # Buscar el usuario por su nombre
        cursor.execute("SELECT photo, idUser FROM user WHERE name = ?", (username,))
        result = cursor.fetchone()

        if result is not None:
            id = result[1]
            
            # Convertir los datos de la foto a un array de NumPy
            photo_data = result[0]
            photo_array = np.frombuffer(photo_data, dtype=np.uint8)

            # Convertir el array de NumPy en una imagen OpenCV
            img = cv2.imdecode(photo_array, cv2.IMREAD_COLOR)
            return img, id
        else:
            return None, None
    except db.Error as e:
        print(f"Error al acceder a la base de datos: {e}")
        return None, None
    finally:
        cursor.close()

def existe_usuario(username):
    # Conectarse a la base de datos
    db = get_db()
    cursor = db.cursor()
    
    # Realizar la consulta
    cursor.execute("SELECT * FROM user WHERE name = ?", (username,))
    user = cursor.fetchone()

    # Si 'user' no es None, entonces el usuario ya existe
    if user:
        return True
    else:
        return False