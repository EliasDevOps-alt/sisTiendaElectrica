from database.db import get_connection

# ─── CATEGORÍAS ────────────────────────────────────────────────
def get_categorias():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categorias ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_categoria(nombre, id=None):
    conn = get_connection()
    if id:
        conn.execute("UPDATE categorias SET nombre=? WHERE id=?", (nombre, id))
    else:
        conn.execute("INSERT INTO categorias (nombre) VALUES (?)", (nombre,))
    conn.commit(); conn.close()

# ─── MARCAS ────────────────────────────────────────────────────
def get_marcas():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM marcas ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_marca(nombre, id=None):
    conn = get_connection()
    if id:
        conn.execute("UPDATE marcas SET nombre=? WHERE id=?", (nombre, id))
    else:
        conn.execute("INSERT INTO marcas (nombre) VALUES (?)", (nombre,))
    conn.commit(); conn.close()

# ─── PRODUCTOS ─────────────────────────────────────────────────
def get_productos(solo_activos=True, busqueda="", categoria_id=None, marca_id=None):
    conn = get_connection()
    query = """
        SELECT p.*, c.nombre as categoria, m.nombre as marca
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN marcas m ON p.marca_id = m.id
        WHERE 1=1
    """
    params = []
    if solo_activos:
        query += " AND p.activo = 1"
    if busqueda:
        query += " AND (p.descripcion LIKE ? OR p.codigo_tienda LIKE ? OR p.codigo_proveedor LIKE ?)"
        params += [f"%{busqueda}%"] * 3
    if categoria_id:
        query += " AND p.categoria_id = ?"
        params.append(categoria_id)
    if marca_id:
        query += " AND p.marca_id = ?"
        params.append(marca_id)
    query += " ORDER BY p.descripcion"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_producto_by_id(id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM productos WHERE id=?", (id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def save_producto(data, id=None):
    conn = get_connection()
    if id:
        conn.execute("""
            UPDATE productos SET codigo_proveedor=?, descripcion=?, categoria_id=?, marca_id=?,
            unidad_medida=?, precio_compra=?, porcentaje_venta=?, precio_venta=?,
            descuento_maximo=?, activo=? WHERE id=?
        """, (data['codigo_proveedor'], data['descripcion'], data['categoria_id'], data['marca_id'],
              data['unidad_medida'], data['precio_compra'], data['porcentaje_venta'],
              data['precio_venta'], data['descuento_maximo'], data['activo'], id))
    else:
        # Generar codigo_tienda consecutivo
        row = conn.execute("SELECT MAX(CAST(SUBSTR(codigo_tienda,2) AS INTEGER)) FROM productos WHERE codigo_tienda LIKE 'P%'").fetchone()
        siguiente = (row[0] or 0) + 1
        codigo = f"P{siguiente:05d}"
        conn.execute("""
            INSERT INTO productos (codigo_tienda, codigo_proveedor, descripcion, categoria_id, marca_id,
            unidad_medida, precio_compra, porcentaje_venta, precio_venta, descuento_maximo, stock, activo)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,1)
        """, (codigo, data['codigo_proveedor'], data['descripcion'], data['categoria_id'],
              data['marca_id'], data['unidad_medida'], data['precio_compra'],
              data['porcentaje_venta'], data['precio_venta'], data['descuento_maximo'],
              data.get('stock', 0)))
    conn.commit(); conn.close()

def toggle_producto_activo(id, activo):
    conn = get_connection()
    conn.execute("UPDATE productos SET activo=? WHERE id=?", (activo, id))
    conn.commit(); conn.close()

# ─── PROVEEDORES ───────────────────────────────────────────────
def get_proveedores():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM proveedores ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_proveedor(data, id=None):
    conn = get_connection()
    if id:
        conn.execute("UPDATE proveedores SET nombre=?,celular=?,direccion=?,porcentaje_descuento=? WHERE id=?",
                     (data['nombre'], data['celular'], data['direccion'], data['porcentaje_descuento'], id))
    else:
        conn.execute("INSERT INTO proveedores (nombre,celular,direccion,porcentaje_descuento) VALUES (?,?,?,?)",
                     (data['nombre'], data['celular'], data['direccion'], data['porcentaje_descuento']))
    conn.commit(); conn.close()

# ─── CLIENTES ──────────────────────────────────────────────────
def get_clientes():
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.*, cc.nombre as categoria, cc.porcentaje_descuento_margen as descuento_cat
        FROM clientes c
        LEFT JOIN categorias_clientes cc ON c.categoria_cliente_id = cc.id
        ORDER BY c.nombre
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_categorias_clientes():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categorias_clientes ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_cliente(data, id=None):
    conn = get_connection()
    try:
        conn.execute("ALTER TABLE clientes ADD COLUMN direccion TEXT DEFAULT ''")
        conn.commit()
    except: pass
    if id:
        conn.execute("UPDATE clientes SET nombre=?,celular=?,ci_nit=?,categoria_cliente_id=?,direccion=? WHERE id=?",
                     (data['nombre'], data['celular'], data['ci_nit'],
                      data['categoria_cliente_id'], data.get('direccion',''), id))
    else:
        conn.execute("INSERT INTO clientes (nombre,celular,ci_nit,categoria_cliente_id,direccion) VALUES (?,?,?,?,?)",
                     (data['nombre'], data['celular'], data['ci_nit'],
                      data['categoria_cliente_id'], data.get('direccion','')))
    conn.commit(); conn.close()

def save_categoria_cliente(nombre, descuento, id=None):
    conn = get_connection()
    if id:
        conn.execute("UPDATE categorias_clientes SET nombre=?,porcentaje_descuento_margen=? WHERE id=?",
                     (nombre, descuento, id))
    else:
        conn.execute("INSERT INTO categorias_clientes (nombre,porcentaje_descuento_margen) VALUES (?,?)",
                     (nombre, descuento))
    conn.commit(); conn.close()

# ─── USUARIOS ──────────────────────────────────────────────────
def get_usuarios():
    conn = get_connection()
    rows = conn.execute("SELECT id,nombre,username,rol FROM usuarios ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_usuario(data, id=None):
    conn = get_connection()
    if id:
        if data.get('password'):
            conn.execute("UPDATE usuarios SET nombre=?,username=?,password=?,rol=? WHERE id=?",
                         (data['nombre'], data['username'], data['password'], data['rol'], id))
        else:
            conn.execute("UPDATE usuarios SET nombre=?,username=?,rol=? WHERE id=?",
                         (data['nombre'], data['username'], data['rol'], id))
    else:
        conn.execute("INSERT INTO usuarios (nombre,username,password,rol) VALUES (?,?,?,?)",
                     (data['nombre'], data['username'], data['password'], data['rol']))
    conn.commit(); conn.close()

def login(username, password):
    conn = get_connection()
    row = conn.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password)).fetchone()
    conn.close()
    return dict(row) if row else None

# ─── COMPRAS ───────────────────────────────────────────────────
def registrar_compra(proveedor_id, detalles, solo_stock=False):
    """
    detalles: list of {producto_id, cantidad, costo_unitario}
    solo_stock=True  → vendedor: solo suma cantidad, no toca precios ni caja
    solo_stock=False → admin:    flujo completo con precios y egreso en caja
    """
    conn = get_connection()

    if solo_stock:
        # Vendedor: INSERT en compras con total=0, y solo suma stock manualmente
        cursor = conn.execute(
            "INSERT INTO compras (proveedor_id, total) VALUES (?, ?)",
            (proveedor_id, 0))
        compra_id = cursor.lastrowid
        for d in detalles:
            conn.execute(
                "INSERT INTO detalle_compras "
                "(compra_id,producto_id,cantidad,costo_unitario,total) "
                "VALUES (?,?,?,?,?)",
                (compra_id, d['producto_id'], d['cantidad'], 0, 0))
            # Solo sumar stock — NO tocar precio_compra ni precio_venta
            conn.execute(
                "UPDATE productos SET stock = stock + ? WHERE id = ?",
                (d['cantidad'], d['producto_id']))
        conn.commit(); conn.close()
        return compra_id

    # Admin: flujo completo (trigger actualiza stock + precios)
    total_compra = sum(d['cantidad'] * d['costo_unitario'] for d in detalles)
    cursor = conn.execute(
        "INSERT INTO compras (proveedor_id, total) VALUES (?, ?)",
        (proveedor_id, total_compra))
    compra_id = cursor.lastrowid
    for d in detalles:
        total = d['cantidad'] * d['costo_unitario']
        conn.execute(
            "INSERT INTO detalle_compras "
            "(compra_id,producto_id,cantidad,costo_unitario,total) "
            "VALUES (?,?,?,?,?)",
            (compra_id, d['producto_id'], d['cantidad'],
             d['costo_unitario'], total))
    conn.execute(
        "INSERT INTO caja (tipo,monto,descripcion,referencia_id) "
        "VALUES ('EGRESO',?,?,?)",
        (total_compra, f"Compra #{compra_id}", compra_id))
    conn.commit(); conn.close()
    return compra_id

def registrar_entrada_stock(detalles):
    """Solo para VENDEDOR: suma cantidad al stock SIN tocar precios ni caja."""
    conn = get_connection()
    # Deshabilitar el trigger para no afectar precios
    conn.execute("DROP TRIGGER IF EXISTS actualizar_stock_compra")
    # Registrar en historial de compras con costo 0
    cursor = conn.execute(
        "INSERT INTO compras (proveedor_id, total) VALUES (NULL, 0)")
    compra_id = cursor.lastrowid
    for d in detalles:
        # Insertar en detalle (referencia) pero actualizar stock manualmente
        conn.execute(
            "INSERT INTO detalle_compras "
            "(compra_id,producto_id,cantidad,costo_unitario,total) VALUES (?,?,?,0,0)",
            (compra_id, d['producto_id'], d['cantidad']))
        # Actualizar SOLO el stock, preservar precios actuales
        conn.execute("""
            UPDATE productos
            SET stock = stock + ?
            WHERE id = ?
        """, (d['cantidad'], d['producto_id']))
    conn.commit(); conn.close()
    return compra_id


def get_compras():
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.id, c.fecha, c.total, p.nombre as proveedor
        FROM compras c LEFT JOIN proveedores p ON c.proveedor_id = p.id
        ORDER BY c.fecha DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_detalle_compra(compra_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT dc.*, p.descripcion, p.codigo_tienda
        FROM detalle_compras dc JOIN productos p ON dc.producto_id = p.id
        WHERE dc.compra_id = ?
    """, (compra_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ─── VENTAS ────────────────────────────────────────────────────
def registrar_venta(cliente_id, usuario_id, tipo_comprobante, detalles):
    """
    detalles: list of {producto_id, cantidad, precio_venta, descuento_aplicado, precio_final}
    - precio_venta     : precio original sin descuento
    - precio_final     : precio ya calculado con la lógica de margen negociable
    - descuento_aplicado: % sobre margen negociable (informativo)
    """
    conn = get_connection()

    # subtotal = suma de totales CON descuento (precio_final * cantidad)
    subtotal        = 0
    subtotal_sin_desc = 0
    for d in detalles:
        precio_f = d.get('precio_final', d['precio_venta'])
        subtotal          += d['cantidad'] * precio_f
        subtotal_sin_desc += d['cantidad'] * d['precio_venta']

    descuento_total = subtotal_sin_desc - subtotal
    iva             = subtotal * 0.13 if tipo_comprobante == 'FACTURA' else 0
    total           = subtotal + iva

    # Agregar columna descuento_total a ventas si no existe
    try:
        conn.execute("ALTER TABLE ventas ADD COLUMN descuento_total REAL DEFAULT 0")
        conn.commit()
    except: pass

    cursor = conn.execute("""
        INSERT INTO ventas (cliente_id,usuario_id,tipo_comprobante,subtotal,iva,total,descuento_total)
        VALUES (?,?,?,?,?,?,?)
    """, (cliente_id, usuario_id, tipo_comprobante, subtotal_sin_desc, iva, total, descuento_total))
    venta_id = cursor.lastrowid

    # Agregar columnas de override si no existen (compatibilidad BD existente)
    for col in ["descripcion_override TEXT", "unidad_medida_override TEXT", "marca_override TEXT"]:
        try:
            conn.execute(f"ALTER TABLE detalle_ventas ADD COLUMN {col}")
            conn.commit()
        except: pass

    for d in detalles:
        precio_f = d.get('precio_final', d['precio_venta'])
        tot_item = d['cantidad'] * precio_f
        conn.execute("""
            INSERT INTO detalle_ventas
            (venta_id,producto_id,cantidad,precio_venta,descuento_aplicado,total,
             descripcion_override,unidad_medida_override,marca_override)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (venta_id, d['producto_id'], d['cantidad'],
              d['precio_venta'], d['descuento_aplicado'], tot_item,
              d.get('descripcion_override') or None,
              d.get('unidad_medida_override') or None,
              d.get('marca_override') or None))

    conn.execute("INSERT INTO caja (tipo,monto,descripcion,referencia_id) VALUES ('INGRESO',?,?,?)",
                 (total, f"Venta #{venta_id}", venta_id))
    conn.commit(); conn.close()
    return venta_id

def get_ventas():
    conn = get_connection()
    # Columnas de compatibilidad
    for col in ["descuento_total REAL DEFAULT 0"]:
        try:
            conn.execute(f"ALTER TABLE ventas ADD COLUMN {col}")
            conn.commit()
        except: pass
    for col in ["direccion TEXT DEFAULT ''", "celular TEXT DEFAULT ''"]:
        try:
            conn.execute(f"ALTER TABLE clientes ADD COLUMN {col}")
            conn.commit()
        except: pass
    rows = conn.execute("""
        SELECT v.id, v.fecha, v.tipo_comprobante,
               v.subtotal, v.iva, v.total,
               COALESCE(v.descuento_total, 0) as descuento_total,
               c.nombre as cliente, u.nombre as usuario,
               COALESCE(c.celular,'') as cliente_celular,
               COALESCE(c.direccion,'') as cliente_direccion,
               COALESCE(c.ci_nit,'') as cliente_ci_nit
        FROM ventas v
        LEFT JOIN clientes c ON v.cliente_id = c.id
        LEFT JOIN usuarios u ON v.usuario_id = u.id
        ORDER BY v.fecha DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_detalle_venta(venta_id):
    conn = get_connection()
    # Agregar columnas si no existen
    for col in ["descripcion_override TEXT", "unidad_medida_override TEXT", "marca_override TEXT"]:
        try:
            conn.execute(f"ALTER TABLE detalle_ventas ADD COLUMN {col}")
            conn.commit()
        except: pass
    rows = conn.execute("""
        SELECT dv.*,
               COALESCE(dv.descripcion_override, p.descripcion) as descripcion,
               p.codigo_tienda,
               COALESCE(p.codigo_proveedor, p.codigo_tienda) as codigo_proveedor,
               COALESCE(dv.unidad_medida_override, p.unidad_medida) as unidad_medida,
               COALESCE(dv.marca_override, m.nombre, '') as marca
        FROM detalle_ventas dv
        JOIN productos p ON dv.producto_id = p.id
        LEFT JOIN marcas m ON p.marca_id = m.id
        WHERE dv.venta_id = ?
    """, (venta_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ─── COTIZACIONES ──────────────────────────────────────────────
def registrar_cotizacion(cliente_id, detalles):
    conn = get_connection()
    for col in ["subtotal REAL DEFAULT 0", "descuento_total REAL DEFAULT 0"]:
        try:
            conn.execute(f"ALTER TABLE cotizaciones ADD COLUMN {col}")
            conn.commit()
        except: pass
    subtotal_sin = sum(d['cantidad'] * d.get('precio_venta_original', d['precio']) for d in detalles)
    total_con    = sum(d['cantidad'] * d['precio'] for d in detalles)
    descuento    = subtotal_sin - total_con
    cursor = conn.execute(
        "INSERT INTO cotizaciones (cliente_id, total, subtotal, descuento_total) VALUES (?,?,?,?)",
        (cliente_id, total_con, subtotal_sin, descuento))
    cot_id = cursor.lastrowid
    # Agregar columnas de override si no existen
    for col in ["descripcion_override TEXT", "unidad_medida_override TEXT", "marca_override TEXT"]:
        try:
            conn.execute(f"ALTER TABLE detalle_cotizaciones ADD COLUMN {col}")
            conn.commit()
        except: pass

    for d in detalles:
        conn.execute(
            "INSERT INTO detalle_cotizaciones "
            "(cotizacion_id,producto_id,cantidad,precio,total,"
            " descripcion_override,unidad_medida_override,marca_override) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (cot_id, d['producto_id'], d['cantidad'], d['precio'],
             d['cantidad'] * d['precio'],
             d.get('descripcion_override') or None,
             d.get('unidad_medida_override') or None,
             d.get('marca_override') or None))
    conn.commit(); conn.close()
    return cot_id

def get_cotizaciones():
    conn = get_connection()
    for col in ["subtotal REAL DEFAULT 0", "descuento_total REAL DEFAULT 0"]:
        try:
            conn.execute(f"ALTER TABLE cotizaciones ADD COLUMN {col}")
            conn.commit()
        except: pass
    for col in ["direccion TEXT DEFAULT ''", "celular TEXT DEFAULT ''"]:
        try:
            conn.execute(f"ALTER TABLE clientes ADD COLUMN {col}")
            conn.commit()
        except: pass
    rows = conn.execute("""
        SELECT q.id, q.fecha, q.estado, q.total,
               COALESCE(q.subtotal,0) as subtotal,
               COALESCE(q.descuento_total,0) as descuento_total,
               c.nombre as cliente,
               COALESCE(c.celular,'') as cliente_celular,
               COALESCE(c.direccion,'') as cliente_direccion,
               COALESCE(c.ci_nit,'') as cliente_ci_nit
        FROM cotizaciones q LEFT JOIN clientes c ON q.cliente_id = c.id
        ORDER BY q.fecha DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_detalle_cotizacion(cot_id):
    conn = get_connection()
    # Agregar columnas si no existen
    for col in ["descripcion_override TEXT", "unidad_medida_override TEXT", "marca_override TEXT"]:
        try:
            conn.execute(f"ALTER TABLE detalle_cotizaciones ADD COLUMN {col}")
            conn.commit()
        except: pass
    rows = conn.execute("""
        SELECT dc.*,
               COALESCE(dc.descripcion_override, p.descripcion) as descripcion,
               COALESCE(p.codigo_proveedor, p.codigo_tienda) as codigo_proveedor,
               p.codigo_tienda,
               COALESCE(dc.unidad_medida_override, p.unidad_medida) as unidad_medida,
               p.precio_venta  as precio_venta_original,
               p.precio_compra,
               p.porcentaje_venta,
               p.descuento_maximo,
               COALESCE(dc.marca_override, m.nombre, '') as marca
        FROM detalle_cotizaciones dc
        JOIN productos p ON dc.producto_id = p.id
        LEFT JOIN marcas m ON p.marca_id = m.id
        WHERE dc.cotizacion_id = ?
    """, (cot_id,)).fetchall()
    conn.close()
    rows_dict = []
    for r in rows:
        d = dict(r)
        # Calcular descuento aplicado comparando precio guardado vs precio original
        po = d.get('precio_venta_original') or d['precio']
        pf = d['precio']
        d['descuento_bs']  = round(po - pf, 2)
        # % sobre margen negociable (inversa de la formula)
        costo        = d['precio_compra']
        margen_total = d['porcentaje_venta']
        piso         = d['descuento_maximo']
        margen_negoc = max(margen_total - piso, 0)
        if costo > 0 and margen_negoc > 0:
            nuevo_margen  = (pf / costo - 1) * 100
            reduccion     = margen_total - nuevo_margen
            pct_sobre_neg = round(reduccion / margen_negoc * 100, 1)
        else:
            pct_sobre_neg = 0
        d['pct_descuento'] = max(0, pct_sobre_neg)
        rows_dict.append(d)
    return rows_dict

def convertir_cotizacion_a_venta(cot_id, usuario_id, tipo_comprobante):
    detalles_cot = get_detalle_cotizacion(cot_id)
    detalles_venta = [{'producto_id': d['producto_id'], 'cantidad': d['cantidad'],
                       'precio_venta': d['precio'], 'descuento_aplicado': 0} for d in detalles_cot]
    conn = get_connection()
    cot = conn.execute("SELECT cliente_id FROM cotizaciones WHERE id=?", (cot_id,)).fetchone()
    conn.close()
    venta_id = registrar_venta(cot['cliente_id'], usuario_id, tipo_comprobante, detalles_venta)
    conn = get_connection()
    conn.execute("UPDATE cotizaciones SET estado='CONVERTIDA' WHERE id=?", (cot_id,))
    conn.commit(); conn.close()
    return venta_id

# ─── CAJA ──────────────────────────────────────────────────────
def get_movimientos_caja(fecha_inicio=None, fecha_fin=None):
    conn = get_connection()
    query = "SELECT * FROM caja WHERE 1=1"
    params = []
    if fecha_inicio:
        query += " AND fecha >= ?"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND fecha <= ?"
        params.append(fecha_fin + " 23:59:59")
    query += " ORDER BY fecha DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_resumen_caja():
    conn = get_connection()
    ingresos = conn.execute("SELECT COALESCE(SUM(monto),0) FROM caja WHERE tipo='INGRESO'").fetchone()[0]
    egresos = conn.execute("SELECT COALESCE(SUM(monto),0) FROM caja WHERE tipo='EGRESO'").fetchone()[0]
    conn.close()
    return {'ingresos': ingresos, 'egresos': egresos, 'saldo': ingresos - egresos}

def registrar_movimiento_manual(tipo, monto, descripcion):
    conn = get_connection()
    conn.execute("INSERT INTO caja (tipo,monto,descripcion) VALUES (?,?,?)", (tipo, monto, descripcion))
    conn.commit(); conn.close()

# ─── INVENTARIO / REPORTES ─────────────────────────────────────
def get_valor_inventario():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.descripcion, p.codigo_tienda, p.stock,
               p.precio_compra, p.precio_venta,
               p.stock * p.precio_compra as valor_inventario,
               (p.precio_venta - p.precio_compra) as ganancia_unitaria,
               p.stock * (p.precio_venta - p.precio_compra) as ganancia_total
        FROM productos p WHERE p.activo=1 ORDER BY p.descripcion
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_stock_bajo(limite=5):
    conn = get_connection()
    rows = conn.execute("""
        SELECT descripcion, codigo_tienda, stock FROM productos
        WHERE activo=1 AND stock <= ? ORDER BY stock ASC
    """, (limite,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
