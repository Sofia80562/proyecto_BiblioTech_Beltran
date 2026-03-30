# C:\Users\sofia\proyecto_BiblioTech_Beltran\app.py
from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import io

from services.usuario_service import obtener_usuario_por_id, validar_usuario, registrar_nuevo_usuario, obtener_conexion
from services.libro_service import listar_libros, insertar_libro, eliminar_libro, generar_reporte_pdf

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mi_llave_secreta_biblio_123'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return obtener_usuario_por_id(user_id)

# --- RUTAS PÚBLICAS ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# --- TABLA 1: LIBROS (CRUD) ---
@app.route('/inventario')
@login_required 
def inventario():
    lista = listar_libros()
    
    # Traemos las categorías de la tabla 'categorias' para el formulario
    db = obtener_conexion()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT nombre_categoria FROM categorias ORDER BY nombre_categoria ASC")
    categorias_list = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('inventario.html', libros=lista, categorias=categorias_list)

@app.route('/agregar', methods=['POST'])
@login_required
def agregar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    categoria = request.form['categoria']  # Captura el género seleccionado del 'select'
    cantidad = request.form['cantidad']
    precio = request.form['precio']
    
    insertar_libro(titulo, autor, cantidad, precio, categoria)
    return redirect(url_for('inventario'))

@app.route('/eliminar/<int:id>')
@login_required 
def eliminar(id):
    eliminar_libro(id)
    return redirect(url_for('inventario'))

# --- TABLA 2: USUARIOS ---
@app.route('/usuarios')
@login_required 
def ver_usuarios():
    db = obtener_conexion()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id_usuario, nombre, email FROM usuarios")
    usuarios_db = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('usuarios.html', usuarios=usuarios_db)

# --- TABLA 3: CATEGORÍAS ---
@app.route('/categorias')
@login_required
def ver_categorias():
    db = obtener_conexion()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT nombre_categoria FROM categorias ORDER BY nombre_categoria ASC")
    lista_categorias = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('categorias.html', categorias=lista_categorias)

# --- REPORTES ---
@app.route('/descargar_reporte')
@login_required
def descargar_reporte():
    libros = listar_libros()
    pdf_datos = generar_reporte_pdf(libros)
    
    if pdf_datos:
        return send_file(
            io.BytesIO(pdf_datos),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='reporte_bibliotech_beltran.pdf'
        )
    return "Error al generar el reporte", 500

# --- SISTEMA DE AUTENTICACIÓN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_obj = validar_usuario(request.form['email'], request.form['password'])
        if user_obj:
            login_user(user_obj)
            return redirect(url_for('inventario'))
        return "Credenciales incorrectas. <a href='/login'>Reintentar</a>"
    return render_template('login.html')

@app.route('/registrar_usuario', methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'POST':
        registrar_nuevo_usuario(
            request.form['nombre'],
            request.form['email'],
            request.form['password']
        )
        return redirect(url_for('login')) 
    return render_template('registro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)