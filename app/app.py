from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    cursos = ["eje1", "eje2", "eje3", "eje4", "eje5", "eje6"]
    data = {
            'titulo': 'index',
            'bienvenida': "hola",
            'cursos': cursos}
    
    return render_template('index.html', data=data)

@app.route('/proyecto/<nombre>/<int:edad>')
def proyecto(nombre, edad=20):
    data = {
            'titulo': 'proyecto',
            'nombre': nombre,
            'edad': edad}
    return render_template('proyecto.html', data=data)

def query_string():
    print(request)
    print(request.args.get('param1'))
    return "ok"

def pagina_no_encontrada(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.add_url_rule('/query_string', view_func=query_string)
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(debug=True)
    