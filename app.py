from flask import Flask, render_template, request, redirect, url_for
from database import agregar_producto, listar_productos, actualizar_producto, eliminar_producto, listar_historial, \
    obtener_producto_por_id, connect_db
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from auth import verificar_usuario, Usuario
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'secret_key_here'
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt()


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


@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if current_user.rol != 'admin':
        return redirect(url_for('index'))  # Redirige a la página principal si no es admin
    return render_template('admin_dashboard.html')

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

if __name__ == '__main__':
    app.run(debug=True)
