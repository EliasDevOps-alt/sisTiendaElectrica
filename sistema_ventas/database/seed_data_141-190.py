import sqlite3
import os
from db import get_connection

def populate_data():
    conn = get_connection()
    cursor = conn.cursor()

    print("--- Iniciando carga de datos (Grupo 3: P00141 - P00190) ---")

    # 1. Asegurar Marcas existentes y registrar las nuevas del listado
    marcas = [
        (13, 'OMEGA'), (14, 'UYUSTOOLS'), 
        (15, 'FORZA'), (16, 'ULIX'), (17, 'CAMSCO')
    ]
    cursor.executemany("INSERT OR IGNORE INTO marcas (id, nombre) VALUES (?, ?)", marcas)

    # 2. Asegurar Categorías existentes y registrar las nuevas del listado
    categorias = [
        (26, 'EXTENSION'), (27, 'CABLES'), (28, 'CABLE CANAL'), 
        (29, 'DIFERENCIAL'), (30, 'ENCHUFES')
    ]
    cursor.executemany("INSERT OR IGNORE INTO categorias (id, nombre) VALUES (?, ?)", categorias)

    # 3. Preparar lista de productos (Análisis de image_d2efdd.png)
    # Formato: (codigo_tienda, codigo_proveedor, descripcion, categoria_id, marca_id, unidad_medida, precio_compra, porcentaje_venta, precio_venta, descuento_maximo, stock)
    productos = [
        ('P00141', '0', 'FOCO RECARGABLE 400W', 25, 1, 'Pieza', 46.0, 32, 60.72, 5, 3),
        ('P00142', '0', 'FOCO RECARGABLE 500W', 25, 1, 'Pieza', 60.0, 32, 79.2, 5, 3),
        ('P00143', '0', 'FOCO BOTELLA 30W', 25, 12, 'Pieza', 17.0, 32, 22.44, 5, 10),
        ('P00144', '0', 'FOCO BOTELLA 40W', 25, 12, 'Pieza', 25.0, 32, 33.0, 5, 10),
        ('P00145', '0', 'FOCO BOTELLA 50W', 25, 12, 'Pieza', 30.0, 32, 39.6, 5, 10),
        ('P00146', '0', 'FOCO BOTELLA 20W', 25, 12, 'Pieza', 12.5, 32, 16.5, 5, 10),
        ('P00147', '0', 'FOCO BOTELLA 15W', 25, 12, 'Pieza', 9.5, 32, 12.54, 5, 10),
        ('P00148', '0', 'EXTENSION OMEGA', 26, 13, 'Pieza', 20.0, 32, 26.4, 5, 2),
        ('P00149', '0', 'EXTENSION UYUSTOOLS 4T', 26, 14, 'Pieza', 49.0, 32, 64.68, 5, 2),
        ('P00150', '0', 'EXTENSION UYUSTOOLS 6T', 26, 14, 'Pieza', 70.0, 32, 92.4, 5, 2),
        ('P00151', '0', 'EXTENSION FORZA', 26, 15, 'Pieza', 37.0, 32, 48.84, 5, 2),
        ('P00152', '0', 'CINTA DE COLO NEGRO 3M', 15, 3, 'Pieza', 7.5, 32, 9.9, 5, 10),
        ('P00153', '0', 'CABLE DE COLOR BLANCO 12 AWG', 27, 16, 'Pieza', 1.05, 32, 1.386, 5, 100),
        ('P00154', '0', 'CABLE DE COLOR BLANCO 10 AWG', 27, 16, 'Pieza', 2.0, 32, 2.64, 5, 100),
        ('P00155', '0', 'TOMA NEMA', 23, 1, 'Pieza', 8.5, 32, 11.22, 5, 10),
        ('P00156', '0', 'CAJA REDONDA DE COLO NEGRO', 23, 1, 'Pieza', 11.0, 32, 14.52, 5, 10),
        ('P00157', '0', 'CABLE CANAL CON PEGAMENTO 15X10', 28, 1, 'Pieza', 4.8, 32, 6.336, 5, 50),
        ('P00158', '0', 'CABLE CANAL CON PEGAMENTO 20X10', 28, 1, 'Pieza', 3.8, 32, 5.016, 5, 50),
        ('P00159', '814009', 'DISYUNTOR TERMOMAGNETICO NXB-63 1P C2 6kA', 6, 2, 'Pieza', 25.056, 32, 33.0739, 5, 2),
        ('P00160', '814011', 'DISYUNTOR TERMOMAGNETICO NXB-63 1P C4 6kA', 6, 2, 'Pieza', 25.056, 32, 33.0739, 5, 2),
        ('P00161', '814012', 'Disyuntor Termomagnetico, 1p, 6 KA, 6 A', 6, 2, 'Pieza', 25.056, 32, 33.0739, 5, 2),
        ('P00162', '816123', 'DISYUNTOR TERMOMAGNETICO NXB-63 1P C80', 6, 2, 'Pieza', 67.6512, 32, 89.2996, 5, 2),
        ('P00163', '816125', 'DISYUNTOR TERMOMAGNETICO NXB-125 1P C100', 6, 2, 'Pieza', 67.6512, 32, 89.2996, 5, 2),
        ('P00164', '816127', 'DISYUNTOR TERMOMAGNETICO NXB-125 1P C125', 6, 2, 'Pieza', 67.6512, 32, 89.2996, 5, 2),
        ('P00165', '814087', 'DISYUNTOR TERMOMAGNETICO NXB-63 2P C2', 6, 2, 'Pieza', 50.112, 32, 66.1478, 5, 2),
        ('P00166', '814089', 'DISYUNTOR TERMOMAGNETICO NXB-63 2P C4', 6, 2, 'Pieza', 50.112, 32, 66.1478, 5, 2),
        ('P00167', '814090', 'Disyuntor Termomagnetico, 2p, 6 KA, 6 A', 6, 2, 'Pieza', 45.1008, 32, 59.5331, 5, 2),
        ('P00168', '816133', 'DISYUNTOR TERMOMAGNETICO NXB-125 2P C80', 6, 2, 'Pieza', 140.3136, 32, 185.214, 5, 2),
        ('P00169', '816131', 'DISYUNTOR TERMOMAGNETICO NXB-63 2P C100', 6, 2, 'Pieza', 140.3136, 32, 185.214, 5, 2),
        ('P00170', '158068', 'Disyuntor Termomagnetico, 3p, 6 kA, 100A', 6, 2, 'Pieza', 207.9648, 32, 274.5135, 5, 2),
        ('P00171', '158105', 'Disyuntor Termomagnetico, 3p, 6 KA, 125A', 6, 2, 'Pieza', 207.9648, 32, 274.5135, 5, 2),
        ('P00172', '179752', 'Disyuntor Termomagnetico, 4p, 6 KA, 63A', 6, 2, 'Pieza', 175.392, 32, 231.5174, 5, 2),
        ('P00173', '179724', 'Disyuntor Termomagnetico, 3p, 6 KA, 63 A Curva D', 6, 2, 'Pieza', 100.224, 32, 132.2957, 5, 2),
        ('P00174', '105544', 'Int. Diferencial 2p, 30 mA, 25 A 4,5K 1P+N', 29, 2, 'Pieza', 85.1904, 32, 112.4513, 5, 2),
        ('P00175', '105546', 'Int. Diferencial 2p, 30 mA, 40 A 4,5K 1P+N', 29, 2, 'Pieza', 90.2016, 32, 119.0661, 5, 2),
        ('P00176', '105548', 'Int. Diferencial 2p, 30 mA, 63 A 4,5K 1P+N', 29, 2, 'Pieza', 90.2016, 32, 119.0661, 5, 2),
        ('P00177', '280802', 'INTERRUPTOR DIFERENCIAL, 6KA, 300MA, 4P, 63A', 29, 2, 'Pieza', 381.8016, 32, 503.9781, 5, 2),
        ('P00178', '280792', 'INTERRUPTOR DIFERENCIAL, 6KA, 30MA, 4P, 63A', 29, 2, 'Pieza', 381.8016, 32, 503.9781, 5, 2),
        ('P00179', '775003', 'Enchufe Riel Din AC 30', 30, 2, 'Pieza', 10.0224, 32, 13.2296, 5, 2),
        ('P00180', '294538', 'Rele Temporizador con regulador giratorio 60s', 13, 2, 'Pieza', 90.2016, 32, 119.0661, 5, 2),
        ('P00181', '294671', 'Rele De Tiempo Y/D; 1.0-10.0 Seg;220vac', 13, 2, 'Pieza', 100.224, 32, 132.2957, 5, 2),
        ('P00182', '1001812', 'Temp. Escaleras 1na, 0-480 Min. 220vac', 13, 2, 'Pieza', 185.2416, 32, 244.5189, 5, 2),
        ('P00183', '0', 'TERMINAL OJAL 10 MM', 17, 17, 'Pieza', 1.0, 32, 1.32, 5, 200),
        ('P00184', '0', 'TERMINAL OJAL 16 MM', 17, 17, 'Pieza', 1.6, 32, 2.112, 5, 200),
        ('P00185', '0', 'TERMINAL OJAL 25 MM', 17, 17, 'Pieza', 1.9, 32, 2.508, 5, 200),
        ('P00186', '0', 'TERMINAL OJAL 35 MM', 17, 17, 'Pieza', 2.7, 32, 3.564, 5, 200),
        ('P00187', '0', 'TERMINAL OJAL 50 MM', 17, 17, 'Pieza', 4.7, 32, 6.204, 5, 50),
        ('P00188', '0', 'TERMINAL OJAL 70 MM', 17, 17, 'Pieza', 6.0, 32, 7.92, 5, 50),
        ('P00189', '0', 'TERMINAL OJAL 95 MM', 17, 17, 'Pieza', 10.0, 32, 13.2, 5, 50),
        ('P00190', '0', 'TERMINAL OJAL 120 MM', 17, 17, 'Pieza', 12.0, 32, 15.84, 5, 50)
    ]

    # 4. Inserción masiva optimizada
    cursor.executemany("""
        INSERT OR REPLACE INTO productos (
            codigo_tienda, codigo_proveedor, descripcion, categoria_id, marca_id, 
            unidad_medida, precio_compra, porcentaje_venta, precio_venta, 
            descuento_maximo, stock, activo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, productos)

    conn.commit()
    conn.close()
    print(f"--- Éxito: {len(productos)} productos del segundo bloque cargados correctamente ---")

if __name__ == "__main__":
    populate_data()