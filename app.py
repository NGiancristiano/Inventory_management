import sqlite3

from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import agregar_producto, listar_productos, actualizar_producto, eliminar_producto, listar_historial, \
    obtener_producto_por_id, connect_db, crear_orden, registrar_cambio_orden
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from auth import verificar_usuario, Usuario
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'secret_key_here'
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt()

# Configurar la ruta de redirección al login
login_manager.login_view = "login"  # Nombre de la función de la vista de login
login_manager.login_message = "Debes iniciar sesión para acceder a esta página."  # Mensaje opcional
login_manager.login_message_category = "warning"  # Categoría de mensajes flash


# Cargar usuario desde la base de datos (Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    conn, cursor = connect_db()
    cursor.execute("SELECT usuario_id, nombre, email, rol FROM usuarios WHERE usuario_id = ?", (user_id,))
    usuario = cursor.fetchone()
    return Usuario(id=usuario[0], nombre=usuario[1], email=usuario[2], rol=usuario[3]) if usuario else None


# Ruta para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        usuario = verificar_usuario(email, password)
        if usuario:
            login_user(usuario)  # Inicia la sesión del usuario
            return redirect(url_for('index'))
        else:
            return "Credenciales incorrectas", 401

    return render_template('login.html')


# Ruta para logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Ruta para registrar usuarios
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Verificar si las contraseñas coinciden
        if password != confirm_password:
            return "Las contraseñas no coinciden", 400

        # Encriptar la contraseña
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insertar el usuario en la base de datos
        conn, cursor = connect_db()
        cursor.execute("INSERT INTO usuarios (nombre, email, password, rol) VALUES (?, ?, ?, ?)",
                       (nombre, email, hashed_password, 'usuario'))  # Rol por defecto 'usuario'
        conn.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.rol != 'admin':
        return redirect(url_for('index'))

    conn, cursor = connect_db()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM productos")
    total_productos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM historial")
    total_movimientos = cursor.fetchone()[0]

    conn.close()

    return render_template('admin_dashboard.html',
                           total_usuarios=total_usuarios,
                           total_productos=total_productos,
                           total_movimientos=total_movimientos)


# Ruta para el dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/agregar', methods=['GET', 'POST'])
@login_required
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        agregar_producto(nombre, descripcion, cantidad, precio)
        return redirect('/listar')
    return render_template('agregar_producto.html')

@app.route('/listar')
@login_required
def listar():
    productos = listar_productos()
    return render_template('listar_productos.html', productos=productos)

@app.route('/actualizar/<int:id_producto>', methods=['GET', 'POST'])
@login_required
def actualizar(id_producto):
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        cantidad = request.form.get('cantidad', type=int)
        precio = request.form.get('precio', type=float)

        # Si el nombre o la descripción están vacíos, no se actualizan
        if nombre == '':
            nombre = None
        if descripcion == '':
            descripcion = None

        # Llamamos a la función para actualizar el producto
        actualizar_producto(id_producto, nombre, descripcion, cantidad, precio)
        return redirect('/listar')

    producto = obtener_producto_por_id(id_producto)
    return render_template('actualizar_producto.html', producto=producto)


@app.route('/confirmar_eliminar/<int:id_producto>', methods=['GET', 'POST'])
@login_required
def confirmar_eliminar(id_producto):
    # Muestra una página de confirmación antes de eliminar un producto
    if request.method == 'POST':
        # Elimina el producto si el usuario confirma
        eliminar_producto(id_producto)
        return redirect(url_for('index'))

    # Si es GET, muestra la página de confirmación
    producto = obtener_producto_por_id(id_producto)
    return render_template('confirmar_eliminar.html', producto=producto)


@app.route('/historial')
@login_required
def historial():
    historial_movimientos = listar_historial()
    return render_template('listar_historial.html', historial=historial_movimientos)


@app.route('/usuarios')
@login_required
def usuarios():
    if current_user.rol != 'admin':
        return redirect(url_for('index'))  # Redirigir si no es admin

    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM usuarios")
    users = cursor.fetchall()
    conn.close()

    return render_template('usuarios.html', usuarios=users)


@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    if current_user.rol != 'admin':
        return redirect(url_for('index'))  # Redirigir si no es admin

    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM usuarios WHERE usuario_id = ?", (id,))
    usuario = cursor.fetchone()

    if not usuario:
        conn.close()
        return redirect(url_for('usuarios'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        rol = request.form['rol']

        cursor.execute("""
            UPDATE usuarios SET nombre = ?, email = ?, rol = ?
            WHERE usuario_id = ?
        """, (nombre, email, rol, id))
        conn.commit()
        conn.close()

        return redirect(url_for('usuarios'))

    conn.close()
    return render_template('editar_usuario.html', usuario=usuario)


@app.route('/eliminar_usuario/<int:id>', methods=['GET', 'POST'])
@login_required
def eliminar_usuario(id):
    if current_user.rol != 'admin':
        return redirect(url_for('index'))  # Redirigir si no es admin

    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM usuarios WHERE usuario_id = ?", (id,))
    usuario = cursor.fetchone()

    if not usuario:
        conn.close()
        return redirect(url_for('usuarios'))

    if request.method == 'POST':
        cursor.execute("DELETE FROM usuarios WHERE usuario_id = ?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('usuarios'))

    conn.close()
    return render_template('eliminar_usuario.html', usuario=usuario)


@app.route('/productos')
def mostrar_productos():
    productos = listar_productos()
    return render_template('productos.html', productos=productos)


@app.route('/agregar_al_carrito/<int:id_producto>', methods=['POST'])
@login_required
def agregar_al_carrito(id_producto):
    cantidad = int(request.form.get('cantidad', 1))  # Asegurar que la cantidad sea int

    if 'carrito' not in session:
        session['carrito'] = {}

    carrito = session['carrito']

    # Convertir las claves del carrito a int para evitar errores de comparación
    carrito = {int(k): v for k, v in carrito.items()}

    # Agregar o actualizar la cantidad
    if id_producto in carrito:
        carrito[id_producto] += cantidad
    else:
        carrito[id_producto] = cantidad

    session['carrito'] = carrito  # Guardar cambios en la sesión
    session.modified = True

    return redirect(url_for('mostrar_productos'))


@app.route('/carrito')
def mostrar_carrito():
    carrito = session.get('carrito', {})
    productos_carrito = []
    total = 0
    if carrito:
        conn, cursor = connect_db()
        for id_producto, cantidad in carrito.items():
            cursor.execute("SELECT * FROM productos WHERE id = ?", (id_producto,))
            producto = cursor.fetchone()
            if producto:
                total += producto[4] * cantidad  # producto[4] es el precio
                productos_carrito.append({
                    'nombre': producto[1],
                    'cantidad': cantidad,
                    'precio': producto[4],
                    'total': producto[4] * cantidad
                })
        conn.close()

    return render_template('carrito.html', productos=productos_carrito, total=total)


@app.route('/crear_orden', methods=['POST'])
@login_required
def crear_orden():
    conn, cursor = connect_db()

    # Obtener productos del carrito
    carrito = session.get('carrito', {})

    if not carrito:
        flash("El carrito está vacío.", "warning")
        return redirect(url_for('ver_carrito'))

    try:
        total = 0  # Variable para almacenar el total de la orden

        # Insertar la orden en la base de datos con un estado inicial "Pendiente"
        cursor.execute("INSERT INTO ordenes (usuario_id, total, estado) VALUES (?, ?, 'Pendiente')",
                       (current_user.id, total))
        orden_id = cursor.lastrowid  # Obtener el ID de la orden recién creada

        # Insertar cada producto en la tabla detalles_orden
        for id_producto, cantidad in carrito.items():
            cursor.execute("SELECT precio FROM productos WHERE id = ?", (id_producto,))
            producto = cursor.fetchone()

            if producto:
                precio_unitario = producto[0]
                subtotal = precio_unitario * cantidad  # Calcular subtotal por producto
                total += subtotal  # Sumar al total de la orden

                cursor.execute("""
                    INSERT INTO detalles_orden (orden_id, producto_id, cantidad, precio_unitario)
                    VALUES (?, ?, ?, ?)
                """, (orden_id, id_producto, cantidad, precio_unitario))

        # Actualizar el total de la orden después de calcularlo
        cursor.execute("UPDATE ordenes SET total = ? WHERE orden_id = ?", (total, orden_id))

        conn.commit()
        session['carrito'] = {}  # Vaciar el carrito después de crear la orden
        flash("Orden creada exitosamente.", "success")
        return redirect(url_for('mostrar_orden', orden_id=orden_id))

    except sqlite3.Error as e:
        conn.rollback()
        flash(f"Error al crear la orden: {e}", "danger")
        return redirect(url_for('ver_carrito'))

    finally:
        conn.close()


@app.route('/orden/<int:orden_id>')
@login_required
def mostrar_orden(orden_id):
    conn, cursor = connect_db()
    cursor.execute("""
        SELECT o.orden_id, o.fecha, o.estado, p.nombre, do.cantidad, do.precio_unitario
        FROM ordenes o
        JOIN detalles_orden do ON o.orden_id = do.orden_id
        JOIN productos p ON do.producto_id = p.id
        WHERE o.orden_id = ?
    """, (orden_id,))
    detalles = cursor.fetchall()
    conn.close()

    return render_template('orden.html', detalles=detalles)


@app.route('/ordenes')
@login_required
def listar_ordenes():
    conn, cursor = connect_db()
    cursor.execute("""
        SELECT o.orden_id, o.fecha, o.total, o.estado, u.nombre
        FROM ordenes o
        JOIN usuarios u ON o.usuario_id = u.usuario_id
    """)
    ordenes = cursor.fetchall()
    conn.close()

    return render_template('listar_ordenes.html', ordenes=ordenes)


@app.route('/editar_orden/<int:orden_id>', methods=['GET', 'POST'])
@login_required
def editar_orden(orden_id):
    if current_user.rol != 'admin':
        return redirect(url_for('index'))  # Solo admin puede editar órdenes

    conn, cursor = connect_db()

    # Obtener la orden y sus detalles
    cursor.execute("SELECT * FROM ordenes WHERE orden_id = ?", (orden_id,))
    orden = cursor.fetchone()

    if not orden:
        conn.close()
        return redirect(url_for('listar_ordenes'))  # Redirige si la orden no existe

    if request.method == 'POST':
        nuevo_estado = request.form['estado']
        cursor.execute("UPDATE ordenes SET estado = ? WHERE orden_id = ?", (nuevo_estado, orden_id))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_ordenes'))  # Redirigir después de actualizar

    conn.close()
    return render_template('editar_orden.html', orden=orden)


@app.route('/editar_detalles_orden/<int:orden_id>', methods=['GET', 'POST'])
@login_required
def editar_detalles_orden(orden_id):
    if current_user.rol != 'admin':
        return redirect(url_for('index'))  # Solo admin puede editar órdenes

    conn, cursor = connect_db()

    try:
        # Obtener la orden
        cursor.execute("SELECT * FROM ordenes WHERE orden_id = ?", (orden_id,))
        orden = cursor.fetchone()

        if not orden:
            return redirect(url_for('listar_ordenes'))  # Redirigir si la orden no existe

        # Obtener los detalles de la orden
        cursor.execute("""
            SELECT d.detalle_id, p.nombre, d.cantidad, d.precio_unitario
            FROM detalles_orden d
            JOIN productos p ON d.producto_id = p.id
            WHERE d.orden_id = ?
        """, (orden_id,))
        detalles = cursor.fetchall()

        # Obtener productos disponibles para agregar
        cursor.execute("SELECT id, nombre, precio FROM productos")
        productos_disponibles = cursor.fetchall()

        if request.method == 'POST':
            for detalle in detalles:
                detalle_id = detalle[0]
                nueva_cantidad = request.form.get(f'cantidad_{detalle_id}')

                if nueva_cantidad and int(nueva_cantidad) > 0:
                    cursor.execute("""
                        UPDATE detalles_orden SET cantidad = ? WHERE detalle_id = ?
                    """, (int(nueva_cantidad), detalle_id))

                    # Registrar el cambio en el historial
                    registrar_cambio_orden(conn, orden_id, current_user.id, "Actualización",
                                           f"Modificó cantidad de '{detalle[1]}' a {nueva_cantidad}")
                else:
                    cursor.execute("""
                        DELETE FROM detalles_orden WHERE detalle_id = ?
                    """, (detalle_id,))

                    # Registrar el cambio en el historial
                    registrar_cambio_orden(conn, orden_id, current_user.id, "Eliminación",
                                           f"Modificó cantidad de '{detalle[1]}' a 0")


            # Agregar un nuevo producto a la orden
            nuevo_producto_id = request.form.get("nuevo_producto")
            nueva_cantidad = request.form.get("nueva_cantidad")

            if nuevo_producto_id and nueva_cantidad and int(nueva_cantidad) > 0:
                cursor.execute("SELECT precio, nombre FROM productos WHERE id = ?", (nuevo_producto_id,))
                precio_unitario, nuevo_producto_nombre = cursor.fetchone()

                cursor.execute("""
                    INSERT INTO detalles_orden (orden_id, producto_id, cantidad, precio_unitario)
                    VALUES (?, ?, ?, ?)
                """, (orden_id, nuevo_producto_id, int(nueva_cantidad), precio_unitario))

                # Registrar el cambio en el historial
                registrar_cambio_orden(conn,orden_id, current_user.id, "Actualización",
                                       f"Se agregó el producto: {nuevo_producto_nombre} con el id: {nuevo_producto_id}")

            # Actualizar el total de la orden
            cursor.execute("""
                SELECT SUM(cantidad * precio_unitario) FROM detalles_orden WHERE orden_id = ?
            """, (orden_id,))
            nuevo_total = cursor.fetchone()[0] or 0

            cursor.execute("UPDATE ordenes SET total = ? WHERE orden_id = ?", (nuevo_total, orden_id))

            conn.commit()

            return redirect(url_for('listar_ordenes'))  # Redirigir después de actualizar
    except sqlite3.OperationalError as e:
        print(f"Error de base de datos: {e}")
        conn.rollback()  # En caso de error, se revierte la transacción
        return "Error al procesar la orden. Por favor, inténtalo más tarde."
    finally:
        conn.close()  # Asegúrate de cerrar la conexión al final
    return render_template('editar_detalles_orden.html', orden=orden, detalles=detalles, productos_disponibles=productos_disponibles)


@app.route('/eliminar_orden/<int:orden_id>',methods=['GET', 'POST'])
@login_required
def eliminar_orden(orden_id):
    if current_user.rol != 'admin':
        return redirect(url_for('index'))  # Solo admin puede editar órdenes

    conn, cursor = connect_db()

    # Obtener la orden y sus detalles
    cursor.execute("SELECT * FROM ordenes WHERE orden_id = ?", (orden_id,))
    orden = cursor.fetchone()

    if not orden:
        conn.close()
        return redirect(url_for('listar_ordenes'))  # Redirige si la orden no existe

    if request.method == 'POST':
        cursor.execute("DELETE FROM ordenes WHERE orden_id = ?", (orden_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_ordenes'))

    conn.close()
    return render_template('eliminar_orden.html', orden=orden)


@app.route('/historial_orden/<int:orden_id>')
@login_required
def historial_orden(orden_id):
    conn, cursor = connect_db()
    cursor.execute("""
        SELECT h.fecha, u.nombre, h.accion, h.detalle_cambio
        FROM historial_ordenes h
        JOIN usuarios u ON h.usuario_id = u.usuario_id
        WHERE h.orden_id = ?
        ORDER BY h.fecha DESC
    """, (orden_id,))
    historial = cursor.fetchall()
    conn.close()

    return render_template('historial_orden.html', historial=historial)


if __name__ == '__main__':
    app.run(debug=True)
