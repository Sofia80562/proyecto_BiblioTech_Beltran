# models/libro.py
class Libro:
    def __init__(self, id, titulo, autor, stock, precio):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.stock = stock
        self.precio = precio