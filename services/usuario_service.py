import mysql.connector
from models.usuario import Usuario

def obtener_conexion():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="", 
        database="biblioteca_db",
        port=3307
    )

def buscar_usuario_por_id(user_id):
    db = obtener_conexion()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    db.close()
    if user_data:
        return Usuario(
            user_data['id_usuario'], 
            user_data['nombre'], 
            user_data['email'], 
            user_data['password']
        )
    return None

def validar_usuario(email, password_ingresada):
    db = obtener_conexion()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    user_data = cursor.fetchone()
    cursor.close()
    db.close()
    if user_data:
        user_obj = Usuario(
            user_data['id_usuario'], 
            user_data['nombre'], 
            user_data['email'], 
            user_data['password']
        )
        if user_obj.verificar_password(password_ingresada):
            return user_obj
    return None

def registrar_nuevo_usuario(nombre, email, password_plano):
    password_cifrado = Usuario.cifrar_password(password_plano)
    db = obtener_conexion()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)", 
        (nombre, email, password_cifrado)
    )
    db.commit()
    cursor.close()
    db.close()