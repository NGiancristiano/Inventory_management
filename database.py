import sqlite3
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


DB_NAME = "inventario.db"

def connect_db():

    # Establece la conexión con la base de datos y devuelve el cursor.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    return conn, cursor


def create_tables():

    #Crea la tabla de productos
    conn, cursor = connect_db()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            descripcion TEXT,
            cantidad INTEGER NOT NULL CHECK (cantidad >= 0),
            precio REAL NOT NULL CHECK (precio >= 0)
        )
    """)

    # Crear la tabla de historial
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial (
                historial_id INTEGER PRIMARY KEY AUTOINCREMENT,
                accion TEXT NOT NULL,
                producto_id INTEGER NOT NULL,
                nombre TEXT,
                descripcion TEXT,
                cantidad INTEGER,
                precio REAL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (producto_id) REFERENCES productos (id)
            )
        """)

    cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    usuario_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    rol TEXT NOT NULL DEFAULT 'usuario',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    conn.commit()
    conn.close()


def registrar_usuario(nombre, email, password, rol='usuario'):
    """Registra un nuevo usuario con contraseña encriptada y rol opcional."""
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    conn, cursor = connect_db()
    try:
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, rol)
            VALUES (?, ?, ?, ?)
        """, (nombre, email, hashed_password, rol))
        conn.commit()
        print(f"Usuario {nombre} registrado exitosamente.")
    except sqlite3.Error as e:
        print(f"Error al registrar el usuario: {e}")
    finally:
        conn.close()


def agregar_producto(nombre, descripcion, cantidad, precio):

    # Agrega un nuevo producto a la base de datos.
    conn, cursor = connect_db()

    try:

        cursor.execute("""
            INSERT INTO productos (nombre, descripcion, cantidad, precio)
            VALUES (?, ?, ?, ?)
        """, (nombre, descripcion, cantidad, precio))

        # Obtener el ID del producto insertado
        producto_id = cursor.lastrowid

        # Registrar el movimiento en el historial
        cursor.execute("""
                    INSERT INTO historial (accion, producto_id, nombre, descripcion, cantidad, precio)
                    VALUES ('Agregar', ?, ?, ?, ?, ?)
                """, (producto_id, nombre, descripcion, cantidad, precio))

        conn.commit()

    except sqlite3.IntegrityError:
        print(f"Error: El producto '{nombre}' ya existe.")
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
    finally:
        conn.close()


def listar_productos():

    # Muestra todos los productos en la base de datos.
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()

    if productos:
        return productos
    else:
        print("No hay productos en el inventario.")


def listar_historial():
    # Muestra el historial de movimientos en la base de datos
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM historial ORDER BY fecha DESC")
    historial = cursor.fetchall()
    conn.close()

    if historial:
        return historial
    else:
        print("No hay historial de movimientos.")


def actualizar_producto(id_producto, nombre=None, descripcion=None, cantidad=None, precio=None):
    """Actualiza un producto en la base de datos con manejo de errores y usando 'with' para conexión."""
    try:
        with sqlite3.connect('inventario.db') as conn:
            cursor = conn.cursor()

            # Verificar si el producto existe antes de intentar actualizar
            cursor.execute("SELECT * FROM productos WHERE id = ?", (id_producto,))
            producto = cursor.fetchone()

            if not producto:
                raise ValueError(f"El producto con ID {id_producto} no existe.")

            cambio = False
            nombre_nuevo = None
            descripcion_nueva = None
            cantidad_vieja = producto[3]
            precio_viejo = producto[4]

            if nombre is not None and nombre != producto[1]:
                cursor.execute("UPDATE productos SET nombre = ? WHERE id = ?", (nombre, id_producto))
                nombre_nuevo = nombre
                cambio = True

            if descripcion is not None and descripcion != producto[2]:
                cursor.execute("UPDATE productos SET descripcion = ? WHERE id = ?", (descripcion, id_producto))
                descripcion_nueva = descripcion
                cambio = True

            if cantidad is not None and cantidad != producto[3]:
                cursor.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (cantidad, id_producto))
                cambio = True

            if precio is not None and precio != producto[4]:
                cursor.execute("UPDATE productos SET precio = ? WHERE id = ?", (precio, id_producto))
                cambio = True

            # Si hubo cambios, registrarlos en el historial
            if cambio:
                cursor.execute("""
                        INSERT INTO historial (accion, producto_id, nombre, descripcion, cantidad, precio) 
                        VALUES (?, ?, ?, ?, ?, ?)
                        """, ("Actualizar", id_producto, nombre_nuevo, descripcion_nueva,cantidad - cantidad_vieja, precio - precio_viejo))

                conn.commit()

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error al actualizar el producto: {e}")


def obtener_producto_por_id(id_producto):
    # Obtiene los detalles de un producto por su ID
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM productos WHERE id = ?", (id_producto,))
    producto = cursor.fetchone()
    conn.close()
    return producto


def eliminar_producto(id_producto):

    # Elimina un producto de la base de datos y registra la accion en el historial
    conn, cursor = connect_db()
    try:

        cursor.execute("SELECT nombre, descripcion, cantidad, precio FROM productos WHERE id = ?", (id_producto,))
        producto = cursor.fetchone()

        if producto:

            nombre, descripcion, cantidad, precio = producto

            cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
            conn.commit()

            # Registrar la eliminación en el historial
            cursor.execute("""
                            INSERT INTO historial (accion, producto_id, nombre, descripcion, cantidad, precio)
                            VALUES ('Eliminar', ?, ?, ?, ?, ?)
                        """, (id_producto, nombre, descripcion, cantidad, precio))
            conn.commit()

        else:
            print(f"No se encontró el producto con ID {id_producto}.")

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")

    finally:
        conn.close()


def crear_admin():
    # Encriptar la contraseña
    password = 'contra123'
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Insertar el usuario admin en la base de datos
    conn, cursor = connect_db()
    cursor.execute("""
        INSERT INTO usuarios (nombre, email, password, rol)
        VALUES (?, ?, ?, ?)
    """, ('Administrador', 'admin@ejemplo.com', hashed_password, 'admin'))
    conn.commit()
    conn.close()

    print("Usuario admin creado correctamente")

if __name__ == "__main__":
    create_tables()