import functools
import os
import cv2
from matplotlib import pyplot as plt

from werkzeug.utils import secure_filename

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# CONFIG
path = "C:/Users/icjardin/Desktop/TrabajoFinalSAPA_IKJB/app/" # your path

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        img = request.files['imagen']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not img:
            error = 'img is required.'

        if error is None:
            
            # filename = secure_filename(img.filename)
            # img_path = os.path.join('./', filename)
            # img.save(img_path)
            # try:
            #     db.execute(
            #         "INSERT INTO user (username, password) VALUES (?, ?)",
            #         (username, generate_password_hash(password)),
            #     )
            #     db.commit()
            # except db.IntegrityError:
            #     error = f"User {username} is already registered."
            # else:
            #     return redirect(url_for("auth.login"))
            print(img)
            try:    
                pic = img.read()
                print(pic)
                if pic:
                    db.execute(
                        "INSERT INTO user (name, photo) VALUES (?, ?)",
                        (username, pic),
                    )
                    db.commit()

            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['imagen']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE name = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        
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
        
def face(img, faces):
    data = plt.imread(img)
    for i in range(len(faces)):
        x1, y1, ancho, alto = faces[i]["box"]
        x2, y2 = x1 + ancho, y1 + alto
        plt.subplot(1,len(faces), i + 1)
        plt.axis("off")
        face = cv2.resize(data[y1:y2, x1:x2],(150,200), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(img, face)
        plt.imshow(data[y1:y2, x1:x2])
    
