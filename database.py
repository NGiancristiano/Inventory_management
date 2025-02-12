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


def actualizar_producto(id_producto, cantidad=None, precio=None):

    # Actualiza la cantidad o precio de un producto en la base de datos.
    conn, cursor = connect_db()

    # Crear la consulta para actualizar
    query = "UPDATE productos SET"
    params = []

    if cantidad is not None:
        query += " cantidad = ?"
        params.append(cantidad)

    if precio is not None:
        if cantidad is not None:
            query += ","
        query += " precio = ?"
        params.append(precio)

    query += " WHERE id = ?"
    params.append(id_producto)

    try:
        cursor.execute(query, params)
        conn.commit()

        if cursor.rowcount > 0:
            print(f"Producto con ID {id_producto} actualizado correctamente.")
        else:
            print(f"No se encontró el producto con ID {id_producto}.")

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")

    finally:
        conn.close()


def eliminar_producto(id_producto):

    # Elimina un producto de la base de datos.
    conn, cursor = connect_db()
    try:
        cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
        conn.commit()

        if cursor.rowcount > 0:
            print(f"Producto con ID {id_producto} eliminado correctamente.")
        else:
            print(f"No se encontró el producto con ID {id_producto}.")

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")

    finally:
        conn.close()


if __name__ == "__main__":
    create_tables()
    eliminar_producto(2)
    listar_productos()