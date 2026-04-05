import io
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from services.libro_service import listar_libros, insertar_libro, eliminar_libro, generar_reporte_pdf, actualizar_libro
from services.usuario_service import validar_usuario, registrar_nuevo_usuario, obtener_conexion, buscar_usuario_por_id
from services.prestamo_service import registrar_prestamo, listar_prestamos

app = Flask(__name__)
app.secret_key = 'clave_secreta_bibliotech_beltran'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return buscar_usuario_por_id(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/inventario')
@login_required 
def inventario():
    lista = listar_libros()
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
    categoria = request.form['categoria']
    cantidad = request.form['cantidad']
    precio = request.form['precio']
    insertar_libro(titulo, autor, cantidad, precio, categoria)
    return redirect(url_for('inventario'))

@app.route('/editar_libro/<int:id>')
@login_required
def editar_libro(id):
    db = obtener_conexion()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM libros WHERE id = %s", (id,))
    libro_encontrado = cursor.fetchone()
    cursor.execute("SELECT DISTINCT nombre_categoria FROM categorias")
    categorias_list = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('editar_libro.html', libro=libro_encontrado, categorias=categorias_list)

@app.route('/actualizar', methods=['POST'])
@login_required
def actualizar():
    id_libro = request.form['id']
    titulo = request.form['titulo']
    autor = request.form['autor']
    categoria = request.form['categoria']
    cantidad = request.form['cantidad']
    precio = request.form['precio']
    actualizar_libro(id_libro, titulo, autor, cantidad, precio, categoria)
    return redirect(url_for('inventario'))

@app.route('/eliminar/<int:id>')
@login_required 
def eliminar(id):
    eliminar_libro(id)
    return redirect(url_for('inventario'))

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

@app.route('/prestamos')
@login_required
def ver_prestamos():
    prestamos_db = listar_prestamos()
    db = obtener_conexion()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id_usuario, nombre FROM usuarios")
    usuarios_list = cursor.fetchall()
    cursor.execute("SELECT id, titulo FROM libros")
    libros_list = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('prestamos.html', prestamos=prestamos_db, usuarios=usuarios_list, libros=libros_list)

@app.route('/nuevo_prestamo', methods=['POST'])
@login_required
def nuevo_prestamo():
    id_usuario = request.form['id_usuario']
    id_libro = request.form['id_libro']
    fecha_devolucion = request.form['fecha_devolucion']
    
    exito = registrar_prestamo(id_usuario, id_libro, fecha_devolucion)
    
    if exito:
        flash("Préstamo registrado con éxito", "success")
    else:
        flash("No hay stock disponible para este libro", "danger")
        
    return redirect(url_for('ver_prestamos'))

if __name__ == '__main__':
    app.run(debug=True)