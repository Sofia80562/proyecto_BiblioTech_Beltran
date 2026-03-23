from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(UserMixin):
    def __init__(self, id, nombre, email, password):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password

    @staticmethod
    def cifrar_password(password):
        return generate_password_hash(password)

    def verificar_password(self, password):
        return check_password_hash(self.password, password)