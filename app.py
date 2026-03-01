from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

class Libro:
    def __init__(self, id, titulo, autor, cantidad, precio):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.cantidad = cantidad
        self.precio = precio

def conectar_db():
    conexion = sqlite3.connect('biblioteca.db', check_same_thread=False)
    conexion.row_factory = sqlite3.Row 
    return conexion

try:
    with conectar_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS productos 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    titulo TEXT NOT NULL, 
                    autor TEXT NOT NULL, 
                    cantidad INTEGER NOT NULL, 
                    precio REAL NOT NULL)''')
        db.commit()
except Exception as e:
    print(f"Error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/inventario')
def inventario():
    db = conectar_db()
    cursor = db.execute('SELECT * FROM productos')
    filas = cursor.fetchall()
    db.close()
    lista_libros = [Libro(f['id'], f['titulo'], f['autor'], f['cantidad'], f['precio']) for f in filas]
    return render_template('inventario.html', libros=lista_libros)

@app.route('/agregar', methods=['POST'])
def agregar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    cantidad = request.form['cantidad']
    precio = request.form['precio']
    
    with conectar_db() as db:
        db.execute('INSERT INTO productos (titulo, autor, cantidad, precio) VALUES (?, ?, ?, ?)',
                   (titulo, autor, cantidad, precio))
    return redirect(url_for('inventario'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    with conectar_db() as db:
        db.execute('DELETE FROM productos WHERE id = ?', (id,))
    return redirect(url_for('inventario'))

if __name__ == '__main__':
    app.run(debug=True)

    
