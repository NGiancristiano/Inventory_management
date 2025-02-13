# Sistema de Gestión de Inventario

Este es un proyecto en desarrollo de un **Sistema de Gestión de Inventario** con funcionalidades adicionales como un **carrito de compras, creación de órdenes** y un **sistema de usuarios con roles personalizables**.

## Características

### 📄 **Módulo de Productos**
- Agregar, editar y eliminar productos.
- Listado de productos con detalles como nombre, descripción, cantidad y precio.
- Historial de movimientos de inventario (registro de cambios en cantidad y eliminaciones).

### 🚀 **Módulo de Usuarios**
- Registro y autenticación de usuarios.
- Sistema de roles (Administrador y Usuario).
- Panel de administración para gestionar usuarios.

### 🛒 **Carrito y Órdenes**
- Agregar productos al carrito.
- Crear órdenes a partir de los productos en el carrito.
- Cambiar el estado de una orden (Pendiente, En proceso, Completada, Cancelada).
- Historial de órdenes para cada usuario.

## Tecnologías Usadas
- **Backend:** Flask (Python) con SQLite (se migrará a MySQL en futuras versiones).
- **Frontend:** HTML, CSS, Bootstrap para el diseño.
- **Autenticación:** Flask-Login para la gestión de usuarios.

## Instalación y Configuración
### 1. Clonar el repositorio
```bash
  git clone https://github.com/NGiancristiano/Inventory_management.git
```

### 2. Crear un entorno virtual e instalar dependencias
```bash
  python -m venv venv
  source venv/bin/activate  # En Windows: venv\Scripts\activate
  pip install -r requirements.txt
```

### 3. Configurar la base de datos
Ejecutar el siguiente comando para crear la base de datos:
```bash
  python database.py
```

### 4. Ejecutar el servidor
```bash
  python app.py
```
La aplicación estará disponible en `http://127.0.0.1:5000`

## Estado del Proyecto
Actualmente, el sistema está **en desarrollo**. Algunas funcionalidades que se planean agregar:
- Exportación de datos (PDF/Excel).
- Notificaciones por correo para cambios en órdenes.
- Mejoras en la interfaz.

## Contribuir
Si deseas contribuir, puedes hacer un fork del repositorio y enviar un pull request con mejoras o correcciones.

## Licencia
Este proyecto está bajo la licencia MIT.

---
🌟 **Desarrollado por:** Nicolas Giancristiano


