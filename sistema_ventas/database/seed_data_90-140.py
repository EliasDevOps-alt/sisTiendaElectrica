import sqlite3
import os
from db import get_connection

def populate_data():
    conn = get_connection()
    cursor = conn.cursor()

    print("--- Iniciando carga de datos iniciales (Grupo 2 - 50 Productos) ---")

    # 1. Insertar Marcas nuevas y existentes
    marcas = [
        (3, '3M'), (4, 'CINCO'), (5, 'BOND'), (6, 'YUSING'), (7, 'SABO'),
        (8, 'FSL'), (9, 'EPEM'), (10, 'ULTRA'), (11, 'LUX'), (12, 'LUXON')
    ]
    cursor.executemany("INSERT OR IGNORE INTO marcas (id, nombre) VALUES (?, ?)", marcas)

    # 2. Insertar Categorías nuevas y existentes
    categorias = [
        (15, 'CINTAS'), (16, 'CAPACITORES'), (17, 'TERMINALES'), (18, 'RIELDIN'),
        (19, 'SPRAY'), (20, 'INTERRUPTORES'), (21, 'TOMACORRIENTES'), (22, 'SOQUET'),
        (23, 'CAJAS'), (24, 'CLAVIJAS'), (25, 'FOCOS')
    ]
    cursor.executemany("INSERT OR IGNORE INTO categorias (id, nombre) VALUES (?, ?)", categorias)

    # 3. Preparar lista de productos (Primeros 50 de la lista)
    # Formato: (codigo_tienda, codigo_proveedor, descripcion, categoria_id, marca_id, unidad_medida, precio_compra, porcentaje_venta, precio_venta, descuento_maximo, stock)
    # Regla: Porcentaje_venta = 32%, Descuento_maximo = 5%, Unidad = 'Pieza'
    productos = [
        ('P00090', '973', 'CINTA VULCANIZANTE SCOTCH 23 5M 19MM X 0.76 - 3M', 15, 3, 'Pieza', 68.0, 32, 89.76, 5, 20),
        ('P00091', '607', 'CINTA AISLANTE SCOTCH SUPER 33+ 20M X 19MM X 0.177MM - 3M', 15, 3, 'Pieza', 76.0, 32, 100.32, 5, 20),
        ('P00092', '227', 'CAPACITOR DE POTENCIA MK9S0.4-10-3 10KVAR 400V 50HZ - CINCO', 16, 4, 'Pieza', 480.0, 32, 633.6, 5, 1),
        ('P00093', '1119', 'TERMINAL PIN TUBULAR 1.5 MM NEGRO ``2E - 1512´´ - BOND', 17, 5, 'Pieza', 0.08, 32, 0.1056, 5, 1100),
        ('P00094', '1120', 'TERMINAL PIN TUBULAR 2.5 MM AZUL ``E - 2512´´ - BOND', 17, 5, 'Pieza', 0.09, 32, 0.1188, 5, 1100),
        ('P00095', '1121', 'TERMINAL PIN TUBULAR 4MM PLOMO ``E - 4012´´ - BOND', 17, 5, 'Pieza', 0.14, 32, 0.1848, 5, 1000),
        ('P00096', '1122', 'TERMINAL PIN TUBULAR 6MM VERDE ``E - 6018´´ - BOND', 17, 5, 'Pieza', 0.19, 32, 0.2508, 5, 1000),
        ('P00097', '56', 'CINTA DE ALGODÓN DE 3/4 ROLLO DE 50M - YUSING', 15, 6, 'Pieza', 45.6, 32, 60.192, 5, 12),
        ('P00098', '1135', 'RIELDIN METALICO 3.5 CM X 1M ``GT - 35ST´´ - BOND', 18, 5, 'Pieza', 20.0, 32, 26.4, 5, 12),
        ('P00099', '171', 'LIMPIA CONTACTO EN SPRAY 590 ML - SABO', 19, 7, 'Pieza', 247.2, 32, 326.304, 5, 14),
        ('P00100', '1129', 'TERMINAL PIN TUBULAR 2 X 1.5MM NEGRO ``T - 2513´´ - BOND', 17, 5, 'Pieza', 0.24, 32, 0.3168, 5, 1000),
        ('P00101', '1130', 'TERMINAL PIN TUBULAR 2 X 2.5MM PLOMO ``T - 2513´´ - BOND', 17, 5, 'Pieza', 0.3, 32, 0.396, 5, 1000),
        ('P00102', '1131', 'TERMINAL PIN TUBULAR 2 X 4MM NARANJA ``T - 4012´´ . BOND', 17, 5, 'Pieza', 0.42, 32, 0.5544, 5, 1000),
        ('P00103', '1132', 'TERMINAL PIN TUBULAR 2 X 6MM AMARILLO ``T - 6014´´ - BOND', 17, 5, 'Pieza', 0.47, 32, 0.6204, 5, 1000),
        ('P00104', '57', 'CINTA DE ALGODÓN DE 1 ROLLO DE 50M - YUSING', 15, 6, 'Pieza', 55.2, 32, 72.864, 5, 12),
        ('P00105', '0', 'INTERRUPTOR DOBLE FSL', 20, 8, 'Pieza', 8.5, 32, 11.22, 5, 20),
        ('P00106', '0', 'TOMA DOBLE FSL', 21, 8, 'Pieza', 8.5, 32, 11.22, 5, 20),
        ('P00107', '0', 'INTERRUTOR MAS TOMA', 20, 1, 'Pieza', 8.5, 32, 11.22, 5, 20),
        ('P00108', '0', 'INTERRUPTOR SIMPLE', 20, 1, 'Pieza', 7.5, 32, 9.9, 5, 20),
        ('P00109', '0', 'TOMA SIMPLE', 21, 1, 'Pieza', 7.5, 32, 9.9, 5, 20),
        ('P00110', '0', 'TOMA 25 A.', 21, 1, 'Pieza', 35.0, 32, 46.2, 5, 10),
        ('P00111', '0', 'TOMA 16 A 4T', 21, 1, 'Pieza', 22.0, 32, 29.04, 5, 10),
        ('P00112', '0', 'TOMA 16 A. 3T', 21, 1, 'Pieza', 19.0, 32, 25.08, 5, 10),
        ('P00113', '0', 'TOMA SIMPLE ECONOMICO', 21, 1, 'Pieza', 3.3, 32, 4.356, 5, 12),
        ('P00114', '0', 'INTERRUPTOR SIMPLE ECNOMICO', 20, 1, 'Pieza', 3.3, 32, 4.356, 5, 25),
        ('P00115', '0', 'SOQUET COLGANTGE EPEM', 22, 9, 'Pieza', 3.5, 32, 4.62, 5, 20),
        ('P00116', '0', 'SOQUET PLATO ULTRA', 22, 10, 'Pieza', 5.5, 32, 7.26, 5, 12),
        ('P00117', '0', 'SOQUET PLATO PEQUEÑO', 22, 10, 'Pieza', 5.0, 32, 6.6, 5, 12),
        ('P00118', '0', 'CAJA SIMPLE SOBREPUESTA PARA INT. O TOMA', 23, 1, 'Pieza', 5.0, 32, 6.6, 5, 20),
        ('P00119', '0', 'CAJA RECTA CR OJO', 23, 1, 'Pieza', 9.5, 32, 12.54, 5, 10),
        ('P00120', '0', 'SOQUET ECONOMICO', 22, 1, 'Pieza', 1.75, 32, 2.31, 5, 20),
        ('P00121', '0', 'SOQUET PORCELANA', 22, 1, 'Pieza', 6.3, 32, 8.316, 5, 20),
        ('P00122', '0', 'CLAVIJA', 24, 1, 'Pieza', 3.0, 32, 3.96, 5, 50),
        ('P00123', '0', 'FOCO DE 9W BLANCO LUX', 25, 11, 'Pieza', 5.5, 32, 7.26, 5, 10),
        ('P00124', '0', 'FOCO DE 9W CALIDO LUX', 25, 11, 'Pieza', 5.5, 32, 7.26, 5, 10),
        ('P00125', '0', 'FOCO DE 12W BLANCO LUX', 25, 11, 'Pieza', 7.5, 32, 9.9, 5, 10),
        ('P00126', '0', 'FOCO DE 12W CALIDO LUX', 25, 11, 'Pieza', 7.5, 32, 9.9, 5, 10),
        ('P00127', '0', 'FOCO DE 9W FSL', 25, 8, 'Pieza', 6.5, 32, 8.58, 5, 10),
        ('P00128', '0', 'FOCO LED 25W FSL', 25, 8, 'Pieza', 22.0, 32, 29.04, 5, 10),
        ('P00129', '0', 'FOCO LED 16W FSL', 25, 8, 'Pieza', 18.0, 32, 23.76, 5, 10),
        ('P00130', '0', 'FOCO DE 25W BLANCO LUXON', 25, 12, 'Pieza', 14.5, 32, 19.14, 5, 10),
        ('P00131', '0', 'FOCO DE 18W BLANCO LUXON', 25, 12, 'Pieza', 11.5, 32, 15.18, 5, 10),
        ('P00132', '0', 'FOCO DE 15W BLANCO LUXON', 25, 12, 'Pieza', 9.5, 32, 12.54, 5, 10),
        ('P00133', '0', 'FOCO DE 5W BLANCO LUXON', 25, 12, 'Pieza', 5.5, 32, 7.26, 5, 10),
        ('P00134', '0', 'FOCO SENSOR 18W', 25, 1, 'Pieza', 18.0, 32, 23.76, 5, 5),
        ('P00135', '0', 'FOCO SENSOR 9W', 25, 1, 'Pieza', 25.0, 32, 33.0, 5, 5),
        ('P00136', '0', 'FOCO CALENTADOR POLLO FSL 150W', 25, 8, 'Pieza', 14.5, 32, 19.14, 5, 25),
        ('P00137', '0', 'FOCO CALENTADOR FSL NEGRO 150W', 25, 8, 'Pieza', 12.0, 32, 15.84, 5, 25),
        ('P00138', '0', 'FOCO CALENTADOR FSL ROJO 150W', 25, 8, 'Pieza', 12.0, 32, 15.84, 5, 25),
        ('P00139', '0', 'FOCO DETECTOR DE BILLETES - NEGRO', 25, 1, 'Pieza', 27.0, 32, 35.64, 5, 5),
        ('P00140', '0', 'FOCO RECARGABLE 300W', 25, 1, 'Pieza', 35.0, 32, 46.2, 5, 3)
    ]

    # 4. Insertar productos usando INSERT OR REPLACE
    cursor.executemany("""
        INSERT OR REPLACE INTO productos (
            codigo_tienda, codigo_proveedor, descripcion, categoria_id, marca_id, 
            unidad_medida, precio_compra, porcentaje_venta, precio_venta, 
            descuento_maximo, stock, activo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, productos)

    conn.commit()
    conn.close()
    print(f"--- Éxito: {len(productos)} productos cargados correctamente ---")

if __name__ == "__main__":
    populate_data()