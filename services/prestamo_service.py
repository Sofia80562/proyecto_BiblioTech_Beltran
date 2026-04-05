from services.usuario_service import obtener_conexion

def registrar_prestamo(id_usuario, id_libro, fecha_devolucion):
    db = obtener_conexion()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT stock FROM libros WHERE id = %s", (id_libro,))
        resultado = cursor.fetchone()
        
        if resultado and resultado[0] > 0:
            query_prestamo = """
                INSERT INTO prestamos (id_usuario, id_libro, fecha_devolucion_esperada, estado) 
                VALUES (%s, %s, %s, 'Activo')
            """
            cursor.execute(query_prestamo, (id_usuario, id_libro, fecha_devolucion))

            query_stock = "UPDATE libros SET stock = stock - 1 WHERE id = %s"
            cursor.execute(query_stock, (id_libro,))
            
            db.commit()
            return True
        else:
            return False
            
    except Exception as e:
        db.rollback()
        print(f"Error al registrar préstamo: {e}")
        return False
    finally:
        cursor.close()
        db.close()

def listar_prestamos():
    db = obtener_conexion()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT u.nombre as usuario, l.titulo as libro, 
               p.fecha_salida, p.fecha_devolucion_esperada, p.estado
        FROM prestamos p
        JOIN usuarios u ON p.id_usuario = u.id_usuario
        JOIN libros l ON p.id_libro = l.id
        ORDER BY p.fecha_salida DESC
    """
    cursor.execute(query)
    lista = cursor.fetchall()
    cursor.close()
    db.close()
    return lista