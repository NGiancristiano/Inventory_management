import sqlite3
from tabulate import tabulate


DB_NAME = "inventario.db"

def connect_db():
    # Establece la conexión con la base de datos y devuelve el cursor.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    return conn, cursor

def create_tables():
    #Crea la tabla de productos si no existe.
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
    conn.commit()
    conn.close()



def agregar_producto(nombre, descripcion, cantidad, precio):

    # Agrega un nuevo producto a la base de datos.
    conn, cursor = connect_db()

    try:
        cursor.execute("""
            INSERT INTO productos (nombre, descripcion, cantidad, precio)
            VALUES (?, ?, ?, ?)
        """, (nombre, descripcion, cantidad, precio))
        conn.commit()
        print(f"Producto '{nombre}' agregado correctamente.")
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
        print(tabulate(productos, headers=["ID", "Nombre", "Descripción", "Cantidad", "Precio"], tablefmt="grid"))
    else:
        print("No hay productos en el inventario.")



if __name__ == "__main__":
    create_tables()
    listar_productos()