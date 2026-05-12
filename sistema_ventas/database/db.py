# ============================================================================
# MÓDULO DE BASE DE DATOS (database/db.py)
# ============================================================================
# Este módulo gestiona la conexión y inicialización de la base de datos SQLite
# Se encarga de crear todas las tablas necesarias para el sistema de ventas
# ============================================================================

# IMPORTACIONES DE MÓDULOS ESTÁNDAR
import sqlite3    # Librería para gestionar base de datos SQLite
import os         # Módulo para operaciones del sistema de archivos
import sys        # Módulo del sistema para detectar si la app está compilada

# ============================================================================
# DETECCIÓN DEL ENTORNO (Desarrollo vs Producción)
# ============================================================================
# Verifica si la aplicación está siendo ejecutada como script Python
# o si está compilada como un archivo .exe (con PyInstaller)

if getattr(sys, 'frozen', False):
    # Caso 1: Aplicación compilada como .exe
    # sys.frozen es True cuando se ejecuta desde un .exe generado por PyInstaller
    BASE_DIR = os.path.dirname(sys.executable)  # Carpeta donde está el .exe
else:
    # Caso 2: Aplicación ejecutada como script Python
    # Obtiene el directorio del archivo actual (db.py)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define la ruta de la carpeta de datos
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Define la ruta completa del archivo de base de datos SQLite
DB_PATH = os.path.join(DATA_DIR, 'sistema.db')




# ============================================================================
# FUNCIÓN: get_connection
# ============================================================================
# Propósito: Obtener una conexión a la base de datos SQLite
# Retorna: Conexión activa a la base de datos
# ============================================================================
def get_connection():
    """
    Establece una conexión con la base de datos SQLite.
    Crea la carpeta de datos si no existe.
    Configura parámetros importantes de SQLite.
    """
    # Crea la carpeta de datos si no existe
    # exist_ok=True evita error si la carpeta ya existe
    os.makedirs(DATA_DIR, exist_ok=True)

    print("📁 DB_PATH:", DB_PATH)  # DEBUG: Muestra la ruta de la BD para verificación

    # Crea una conexión con SQLite en la ruta especificada
    conn = sqlite3.connect(DB_PATH)
    
    # Permite que los resultados se devuelvan como objetos Row (acceso por nombre de columna)
    # sin esto, los resultados serían tuplas sin acceso por nombre
    conn.row_factory = sqlite3.Row
    
    # Habilita las restricciones de claves foráneas (FOREIGN KEY)
    # Por defecto SQLite no las valida, esto lo activa
    conn.execute("PRAGMA foreign_keys = ON")
    
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS marcas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS categorias_clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        porcentaje_descuento_margen REAL NOT NULL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_tienda TEXT UNIQUE,
        codigo_proveedor TEXT,
        descripcion TEXT,
        categoria_id INTEGER,
        marca_id INTEGER,
        unidad_medida TEXT DEFAULT 'UNIDAD',
        precio_compra REAL DEFAULT 0,
        porcentaje_venta REAL DEFAULT 0,
        precio_venta REAL DEFAULT 0,
        descuento_maximo REAL DEFAULT 0,
        stock INTEGER DEFAULT 0,
        activo INTEGER DEFAULT 1,
        FOREIGN KEY (categoria_id) REFERENCES categorias(id),
        FOREIGN KEY (marca_id) REFERENCES marcas(id)
    );
    CREATE TABLE IF NOT EXISTS proveedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        celular TEXT,
        direccion TEXT,
        porcentaje_descuento REAL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        celular TEXT,
        ci_nit TEXT,
        categoria_cliente_id INTEGER,
        FOREIGN KEY (categoria_cliente_id) REFERENCES categorias_clientes(id)
    );
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        username TEXT UNIQUE,
        password TEXT,
        rol TEXT CHECK(rol IN ('ADMIN','VENDEDOR'))
    );
    CREATE TABLE IF NOT EXISTS compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proveedor_id INTEGER,
        fecha TEXT DEFAULT CURRENT_TIMESTAMP,
        total REAL DEFAULT 0,
        FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
    );
    CREATE TABLE IF NOT EXISTS detalle_compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        compra_id INTEGER,
        producto_id INTEGER,
        cantidad INTEGER,
        costo_unitario REAL,
        total REAL,
        FOREIGN KEY (compra_id) REFERENCES compras(id),
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    );
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        usuario_id INTEGER,
        fecha TEXT DEFAULT CURRENT_TIMESTAMP,
        tipo_comprobante TEXT CHECK(tipo_comprobante IN ('FACTURA','SIN_FACTURA')),
        subtotal REAL DEFAULT 0,
        iva REAL DEFAULT 0,
        total REAL DEFAULT 0,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    );
    CREATE TABLE IF NOT EXISTS detalle_ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER,
        producto_id INTEGER,
        cantidad INTEGER,
        precio_venta REAL,
        descuento_aplicado REAL DEFAULT 0,
        total REAL,
        FOREIGN KEY (venta_id) REFERENCES ventas(id),
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    );
    CREATE TABLE IF NOT EXISTS cotizaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        fecha TEXT DEFAULT CURRENT_TIMESTAMP,
        estado TEXT DEFAULT 'ACTIVA' CHECK(estado IN ('ACTIVA','CONVERTIDA')),
        total REAL DEFAULT 0,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    );
    CREATE TABLE IF NOT EXISTS detalle_cotizaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cotizacion_id INTEGER,
        producto_id INTEGER,
        cantidad INTEGER,
        precio REAL,
        total REAL,
        FOREIGN KEY (cotizacion_id) REFERENCES cotizaciones(id),
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    );
    CREATE TABLE IF NOT EXISTS caja (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT CHECK(tipo IN ('INGRESO','EGRESO')),
        monto REAL,
        descripcion TEXT,
        referencia_id INTEGER,
        fecha TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.executescript("""
    DROP TRIGGER IF EXISTS actualizar_stock_compra;
    CREATE TRIGGER actualizar_stock_compra
    AFTER INSERT ON detalle_compras
    BEGIN
        UPDATE productos
        SET stock = stock + NEW.cantidad,
            precio_compra = NEW.costo_unitario,
            precio_venta = ROUND(NEW.costo_unitario + (NEW.costo_unitario * porcentaje_venta / 100.0), 2)
        WHERE id = NEW.producto_id;
    END;

    DROP TRIGGER IF EXISTS actualizar_stock_venta;
    CREATE TRIGGER actualizar_stock_venta
    AFTER INSERT ON detalle_ventas
    BEGIN
        UPDATE productos
        SET stock = stock - NEW.cantidad
        WHERE id = NEW.producto_id;
    END;
    """)

    cursor.execute("INSERT OR IGNORE INTO usuarios (id,nombre,username,password,rol) VALUES (1,'Administrador','admin','admin123','ADMIN')")
    cursor.execute("INSERT OR IGNORE INTO categorias (id,nombre) VALUES (1,'General')")
    cursor.execute("INSERT OR IGNORE INTO marcas (id,nombre) VALUES (1,'Sin marca')")
    cursor.execute("INSERT OR IGNORE INTO categorias_clientes (id,nombre,porcentaje_descuento_margen) VALUES (1,'Regular',0)")
    cursor.execute("INSERT OR IGNORE INTO categorias_clientes (id,nombre,porcentaje_descuento_margen) VALUES (2,'Mayorista',10)")
    cursor.execute("INSERT OR IGNORE INTO clientes (id,nombre,celular,ci_nit,categoria_cliente_id) VALUES (1,'Cliente General','','0',1)")
    conn.commit()
    conn.close()
