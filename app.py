from flask import Flask, render_template, request, redirect, url_for
from database import agregar_producto, listar_productos, actualizar_producto, eliminar_producto, listar_historial, \
    obtener_producto_por_id

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        agregar_producto(nombre, descripcion, cantidad, precio)
        return redirect(url_for('index'))
    return render_template('agregar_producto.html')

@app.route('/listar')
def listar():
    productos = listar_productos()
    return render_template('listar_productos.html', productos=productos)

@app.route('/actualizar/<int:id_producto>', methods=['GET', 'POST'])
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
        return redirect(url_for('index'))

    producto = obtener_producto_por_id(id_producto)
    return render_template('actualizar_producto.html', producto=producto)


@app.route('/confirmar_eliminar/<int:id_producto>', methods=['GET', 'POST'])
def confirmar_eliminar(id_producto):
    # Muestra una página de confirmación antes de eliminar un producto
    if request.method == 'POST':
        # Elimina el producto si el usuario confirma
        eliminar_producto(id_producto)
        return redirect(url_for('index'))

    # Si es GET, muestra la página de confirmación
    producto = obtener_producto_por_id(id_producto)
    return render_template('confirmar_eliminar.html', producto=producto)



@app.route('/eliminar', methods=['POST'])
def eliminar():
    id_producto = int(request.form['id_producto'])
    eliminar_producto(id_producto)
    return redirect(url_for('index'))

@app.route('/historial')
def historial():
    historial_movimientos = listar_historial()
    return render_template('listar_historial.html', historial=historial_movimientos)

if __name__ == '__main__':
    app.run(debug=True)
