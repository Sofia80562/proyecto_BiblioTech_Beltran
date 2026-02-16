from flask import Flask

app = Flask(__name__)

# Ruta principal con el nombre de tu negocio
@app.route('/')
def home():
    return """
    <h1>BiblioTech Beltrán - Sistema de Biblioteca</h1>
    <p>Bienvenido a nuestra plataforma de gestión y consulta de libros.</p>
    <hr>
    <p>Prueba las rutas dinámicas para ver cómo funciona el sistema:</p>
    <ul>
        <li>Escribe en la URL: <code>/libro/don-quijote</code></li>
        <li>Escribe en la URL: <code>/libro/el-principito</code></li>
    </ul>
    """

# Ruta dinámica para libros
@app.route('/libro/<titulo>')
def consultar_libro(titulo):
    # Formateamos el título (ej: de 'don-quijote' a 'Don Quijote')
    nombre_limpio = titulo.replace('-', ' ').title()
    return f"<h2>Consulta de Libro</h2><p>Título: <strong>{nombre_limpio}</strong> - Estado: <span style='color:green;'>Disponible en Estantería A1</span>.</p>"

if __name__ == '__main__':
    app.run(debug=True)