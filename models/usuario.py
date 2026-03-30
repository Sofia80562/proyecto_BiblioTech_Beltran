from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, password):
        self.id = id_usuario  
        self.nombre = nombre
        self.email = email
        self.password = password 

    @staticmethod
    def cifrar_password(password_plano):
        """Convierte la contraseña en un hash seguro"""
        return generate_password_hash(password_plano)

    def verificar_password(self, password_ingresada):
        """Compara la contraseña ingresada con el hash guardado"""
        return check_password_hash(self.password, password_ingresada)