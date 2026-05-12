import sqlite3
import os
from db import get_connection

def populate_data():
    conn = get_connection()
    cursor = conn.cursor()

    print("--- Iniciando carga de datos final (P00191 - P00214) ---")

    # 1. Asegurar Marcas (Incluyendo HAROK que aparece al final)
    marcas = [
        (17, 'CAMSCO'), 
        (18, 'HAROK')
    ]
    cursor.executemany("INSERT OR IGNORE INTO marcas (id, nombre) VALUES (?, ?)", marcas)

    # 2. Asegurar Categorías para este bloque
    categorias = [
        (31, 'PRECINTOS'), 
        (32, 'EPOXI'), 
        (17, 'TERMINALES'), 
        (33, 'TUBO DE EMPALME'), 
        (34, 'FUSIBLES')
    ]
    cursor.executemany("INSERT OR IGNORE INTO categorias (id, nombre) VALUES (?, ?)", categorias)

    # 3. Lista de productos extraída de la imagen image_d28660.png
    # Formato: (codigo_tienda, codigo_proveedor, descripcion, categoria_id, marca_id, unidad_medida, precio_compra, porcentaje_venta, precio_venta, descuento_maximo, stock)
    productos = [
        ('P00191', '0', 'PRECINTO 100 MM BLANCO', 31, 17, 'Pieza', 5.0, 32, 6.6, 5, 2),
        ('P00192', '0', 'PRECINTO 100 MM NEGRO', 31, 17, 'Pieza', 5.0, 32, 6.6, 5, 2),
        ('P00193', '0', 'PRECINTO 150 MM BLANCO', 31, 17, 'Pieza', 12.0, 32, 15.84, 5, 2),
        ('P00194', '0', 'PRECINTO 150 MM NEGRO', 31, 17, 'Pieza', 12.0, 32, 15.84, 5, 2),
        ('P00195', '0', 'PRECINTO 200 MM BLANCO', 31, 17, 'Pieza', 23.0, 32, 30.36, 5, 2),
        ('P00196', '0', 'PRECINTO 200 MM NEGRO', 31, 17, 'Pieza', 23.0, 32, 30.36, 5, 2),
        ('P00197', '0', 'PRECINTO 250 MM BLANCO', 31, 17, 'Pieza', 26.0, 32, 34.32, 5, 2),
        ('P00198', '0', 'PRECINTO 250 MM NEGRO', 31, 17, 'Pieza', 26.0, 32, 34.32, 5, 2),
        ('P00199', '0', 'PRECINTO 300 MM BLANCO', 31, 17, 'Pieza', 32.0, 32, 42.24, 5, 2),
        ('P00200', '0', 'PRECINTO 300 MM NEGRO', 31, 17, 'Pieza', 32.0, 32, 42.24, 5, 2),
        ('P00201', '0', 'EPOXI 5x25', 32, 17, 'Pieza', 3.5, 32, 4.62, 5, 20),
        ('P00202', '0', 'EPOXI 5x30', 32, 17, 'Pieza', 5.0, 32, 6.6, 5, 10),
        ('P00203', '0', 'EPOXI 5x35', 32, 17, 'Pieza', 6.0, 32, 7.92, 5, 20),
        ('P00204', '0', 'EPOXI 5x40', 32, 17, 'Pieza', 7.0, 32, 9.24, 5, 20),
        ('P00205', '0', 'EPOXI 5x51', 32, 17, 'Pieza', 9.0, 32, 11.88, 5, 10),
        ('P00206', '0', 'TERMINAL OJAL ROJO', 17, 17, 'Pieza', 0.36, 32, 0.4752, 5, 100),
        ('P00207', '0', 'TERMINAL OJAL AZUL', 17, 17, 'Pieza', 0.4, 32, 0.528, 5, 100),
        ('P00208', '0', 'TERMINAL OJAL AMARILLO', 17, 17, 'Pieza', 0.83, 32, 1.0956, 5, 100),
        ('P00209', '0', 'TERMINAL OJAL AMARILLO 6MM', 17, 17, 'Pieza', 0.92, 32, 1.2144, 5, 100),
        ('P00210', '0', 'TUBO DE EMPALME 4MM', 33, 17, 'Pieza', 1.5, 32, 1.98, 5, 10),
        ('P00211', '0', 'TUBO DE EMPALME 10MM', 33, 17, 'Pieza', 2.0, 32, 2.64, 5, 10),
        ('P00212', '0', 'TUBO DE EMPALME 16MM', 33, 17, 'Pieza', 2.5, 32, 3.3, 5, 10),
        ('P00213', '0', 'FUSIBLE TIPO TUBO', 34, 18, 'Pieza', 7.0, 32, 9.24, 5, 10),
        ('P00214', '0', 'FUSIBLE TIPO TUBO NEUTRO', 34, 18, 'Pieza', 6.0, 32, 7.92, 5, 10)
    ]

    # 4. Inserción masiva
    cursor.executemany("""
        INSERT OR REPLACE INTO productos (
            codigo_tienda, codigo_proveedor, descripcion, categoria_id, marca_id, 
            unidad_medida, precio_compra, porcentaje_venta, precio_venta, 
            descuento_maximo, stock, activo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, productos)

    conn.commit()
    conn.close()
    print(f"--- Carga finalizada: {len(productos)} productos insertados correctamente ---")

if __name__ == "__main__":
    populate_data()