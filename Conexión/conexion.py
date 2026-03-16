import mysql.connector

def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin123", 
        database="biblioteca_db"
    )
