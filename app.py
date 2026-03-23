from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from Conexión.conexion import obtener_conexion

# --- SEMANA 14 ---
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import Usuario

app = Flask(__name__)

# --- CONFIGURACIÓN DE sEGURIDAD ---
app.config['SECRET_KEY'] = 'mi_llave_secreta_biblio_123'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Si alguien no está logueado, lo manda aquí

@login_manager.user_loader
def load_user(user_id):
    db = obtener_conexion()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    db.close()
    if user_data:
        return Usuario(user_data['id_usuario'], user_data['nombre'], user_data['email'], user_data['password'])
    return None

class Libro:
    def __init__(self, id, titulo, autor, stock, precio):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.stock = stock
        self.precio = precio

# --- RUTAS GENERALES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# --- RUTAS PROTEGIDAS CON @login_required ---
@app.route('/inventario')
@login_required 
def inventario():
    db = obtener_conexion()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM libros')
    filas = cursor.fetchall()
    db.close()
    lista_libros = [Libro(f['id'], f['titulo'], f['autor'], f['stock'], f['precio']) for f in filas]
    return render_template('inventario.html', libros=lista_libros)

@app.route('/agregar', methods=['POST'])
@login_required
def agregar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    stock = request.form['cantidad'] 
    precio = request.form['precio']
    
    db = obtener_conexion()
    cursor = db.cursor()
    cursor.execute('INSERT INTO libros (titulo, autor, stock, precio) VALUES (%s, %s, %s, %s)',
                   (titulo, autor, stock, precio))
    db.commit()
    db.close()
    return redirect(url_for('inventario'))

# --- SISTEMA DE AUTENTICACIÓN (LOGIN/LOGOUT/REGISTRO) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_ingresada = request.form['password']
        
        db = obtener_conexion()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        db.close()

        if user_data:
            user_obj = Usuario(user_data['id_usuario'], user_data['nombre'], user_data['email'], user_data['password'])
            
            if user_obj.verificar_password(password_ingresada):
                login_user(user_obj)
                return redirect(url_for('inventario'))
        
        return "Credenciales incorrectas. <a href='/login'>Reintentar</a>"
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/registrar_usuario', methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email'] 
        password_plano = request.form['password']
        
        password_cifrado = Usuario.cifrar_password(password_plano)
        
        db = obtener_conexion()
        cursor = db.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)", 
                       (nombre, email, password_cifrado))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('login')) 
    return render_template('registro.html')

@app.route('/usuarios')
@login_required
def ver_usuarios():
    db = obtener_conexion()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios_db = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('usuarios.html', usuarios=usuarios_db)

@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    db = obtener_conexion()
    cursor = db.cursor()
    # Asegúrate de que la columna se llame 'id' en tu tabla de MySQL
    cursor.execute('DELETE FROM libros WHERE id = %s', (id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for('inventario'))

if __name__ == '__main__':
    app.run(debug=True)