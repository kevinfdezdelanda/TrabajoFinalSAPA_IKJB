import os

from flask import  Flask, render_template, request, send_from_directory
from . import auth, db,chatbot

from guiribot.logger import app_logger

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'guiribot_db.sqlite'),
)

@app.errorhandler(404)
def page_not_found(error):
    app_logger.error("Error en la ruta: {}".format(error))
    return render_template('404.html'), 404

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# def query_string():
#     print(request)
#     print(request.args.get('param1'))
#     return "ok"

# Mejor integrado en chatbot.py
# @app.route('/app/wav/<path:filename>')
# def serve_wav(filename):
#     return send_from_directory('wav', filename)


app.register_blueprint(auth.bp)

app.register_blueprint(chatbot.bp)
app.add_url_rule('/', endpoint='index')

db.init_app(app)

if __name__ == '__main__':
    # app.add_url_rule('/query_string', view_func=query_string)
    # app.register_error_handler(404, pagina_no_encontrada)
    app.run(debug=True)