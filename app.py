from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from Conexión.conexion import obtener_conexion

app = Flask(__name__)

class Libro:
    def __init__(self, id, titulo, autor, stock, precio):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.stock = stock
        self.precio = precio

# --- CONFIGURACIÓN SQLITE (Se mantiene por compatibilidad) ---
def conectar_db():
    conexion = sqlite3.connect('biblioteca.db')
    conexion.row_factory = sqlite3.Row 
    return conexion

# --- RUTAS GENERALES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/inventario')
def inventario():
    # Consultar libros en MySQL
    db = obtener_conexion()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM libros')
    filas = cursor.fetchall()
    db.close()
    lista_libros = [Libro(f['id'], f['titulo'], f['autor'], f['stock'], f['precio']) for f in filas]
    return render_template('inventario.html', libros=lista_libros)

@app.route('/agregar', methods=['POST'])
def agregar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    # CORRECCIÓN: Leemos 'cantidad' del HTML y lo guardamos en 'stock' de la DB
    stock = request.form['cantidad'] 
    precio = request.form['precio']
    
    db = obtener_conexion()
    cursor = db.cursor()
    cursor.execute('INSERT INTO libros (titulo, autor, stock, precio) VALUES (%s, %s, %s, %s)',
                   (titulo, autor, stock, precio))
    db.commit()
    db.close()
    return redirect(url_for('inventario'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db = obtener_conexion()
    cursor = db.cursor()
    cursor.execute('DELETE FROM libros WHERE id = %s', (id,))
    db.commit()
    db.close()
    return redirect(url_for('inventario'))

# --- NUEVAS RUTAS SEMANA 13 (USUARIOS MYSQL) ---

@app.route('/registrar_usuario', methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        mail = request.form['mail']
        password = request.form['password']
        
        db = obtener_conexion()
        cursor = db.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, mail, password) VALUES (%s, %s, %s)", 
                       (nombre, mail, password))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('ver_usuarios'))
    return render_template('registro.html')

@app.route('/usuarios')
def ver_usuarios():
    db = obtener_conexion()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios_db = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('usuarios.html', usuarios=usuarios_db)

# --- INICIO DE LA APP ---
if __name__ == '__main__':
    app.run(debug=True)