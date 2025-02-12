from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from database import connect_db

bcrypt = Bcrypt()

class Usuario(UserMixin):
    def __init__(self, id, nombre, email, rol):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.rol = rol

def verificar_usuario(email, password):
    """Verifica el email y la contraseña del usuario."""
    conn, cursor = connect_db()
    cursor.execute("SELECT usuario_id, nombre, email, password, rol FROM usuarios WHERE email = ?", (email,))
    usuario = cursor.fetchone()

    if usuario and bcrypt.check_password_hash(usuario[3], password):
        # Si la contraseña es correcta, devolvemos un objeto Usuario
        return Usuario(id=usuario[0], nombre=usuario[1], email=usuario[2], rol=usuario[4])
    return None
