# C:\Users\sofia\proyecto_BiblioTech_Beltran\services\libro_service.py
from services.usuario_service import obtener_conexion

def insertar_libro(titulo, autor, cantidad, precio, categoria):
    """
    Inserta un nuevo libro en la base de datos biblioteca_db.
    Asegura que los nombres de las columnas coincidan con la estructura física.
    """
    db = obtener_conexion()
    cursor = db.cursor()
    
    sql = """
        INSERT INTO libros (titulo, autor, categoria, stock, precio) 
        VALUES (%s, %s, %s, %s, %s)
    """
    

    valores = (titulo, autor, categoria, cantidad, precio)
    
    try:
        cursor.execute(sql, valores)
        db.commit()
        print("Libro insertado correctamente.")
    except Exception as e:
        print(f"Error al insertar libro: {e}")
        db.rollback()
    finally:
        cursor.close()
        db.close()

def listar_libros():
    """
    Obtiene todos los libros registrados para mostrarlos en la tabla de inventario.
    """
    db = obtener_conexion()
    # dictionary=True es vital para que Jinja2 reconozca {{ libro.categoria }}
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM libros")
        libros = cursor.fetchall()
        return libros
    except Exception as e:
        print(f"Error al listar libros: {e}")
        return []
    finally:
        cursor.close()
        db.close()

def eliminar_libro(id_libro):
    """
    Elimina un libro por su ID.
    """
    db = obtener_conexion()
    cursor = db.cursor()
    
    sql = "DELETE FROM libros WHERE id = %s"
    
    try:
        cursor.execute(sql, (id_libro,))
        db.commit()
    except Exception as e:
        print(f"Error al eliminar: {e}")
        db.rollback()
    finally:
        cursor.close()
        db.close()

# services/libro_service.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def generar_reporte_pdf(libros):
    """
    Crea un archivo PDF en memoria con el inventario de libros.
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Título del reporte
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "Reporte de Inventario - BiblioTech Beltrán")
    
    p.setFont("Helvetica", 12)
    y = height - 80
    
    # Encabezados de la tabla
    p.drawString(50, y, "ID")
    p.drawString(100, y, "Título")
    p.drawString(300, y, "Autor")
    p.drawString(450, y, "Género")
    p.drawString(530, y, "Precio")
    
    y -= 20
    p.line(50, y + 15, 580, y + 15)

    # Listado de libros
    for libro in libros:
        if y < 50:  # Si se acaba la página, creamos otra
            p.showPage()
            y = height - 50
            
        p.drawString(50, y, str(libro['id']))
        p.drawString(100, y, str(libro['titulo'])[:30])
        p.drawString(300, y, str(libro['autor'])[:20])
        p.drawString(450, y, str(libro.get('categoria', 'General')))
        p.drawString(530, y, f"${libro['precio']:.2f}")
        y -= 20

    p.showPage()
    p.save()
    
    pdf_out = buffer.getvalue()
    buffer.close()
    return pdf_out

def actualizar_libro(id_libro, titulo, autor, cantidad, precio, categoria):
    db = obtener_conexion()
    cursor = db.cursor()
    query = """
        UPDATE libros 
        SET titulo = %s, autor = %s, categoria = %s, stock = %s, precio = %s 
        WHERE id = %s
    """
    cursor.execute(query, (titulo, autor, categoria, cantidad, precio, id_libro))
    db.commit()
    cursor.close()
    db.close()