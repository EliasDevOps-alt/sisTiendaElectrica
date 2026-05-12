from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import os, datetime

EMPRESA   = "LOPEZ ELECTRIC"
EMPRESA_TELEFONO  = ""
EMPRESA_DIRECCION = ""

# ── Estilos ────────────────────────────────────────────────────
def _s():
    return {
        'titulo':     ParagraphStyle('t1',  fontSize=16, fontName='Helvetica-Bold',
                                     alignment=TA_CENTER, textColor=colors.HexColor('#1a1a2e')),
        'subtitulo':  ParagraphStyle('t2',  fontSize=10, fontName='Helvetica',
                                     alignment=TA_CENTER, textColor=colors.grey),
        'normal':     ParagraphStyle('t3',  fontSize=9,  fontName='Helvetica'),
        'bold':       ParagraphStyle('t4',  fontSize=9,  fontName='Helvetica-Bold'),
        'right':      ParagraphStyle('t5',  fontSize=9,  fontName='Helvetica',
                                     alignment=TA_RIGHT),
        'bold_right': ParagraphStyle('t6',  fontSize=10, fontName='Helvetica-Bold',
                                     alignment=TA_RIGHT),
        'label':      ParagraphStyle('t7',  fontSize=8,  fontName='Helvetica',
                                     textColor=colors.grey),
        'desc':       ParagraphStyle('t8',  fontSize=8,  fontName='Helvetica',
                                     leading=10),
    }

# ── Tabla de detalle compartida ─────────────────────────────────
# Columnas: Cód. | Descripción | Cant. | P.U. | Total
def _tabla_detalle(filas, s):
    """
    filas: list of dicts con claves:
        cod, descripcion, cantidad, unidad_medida, precio_unitario, total_item
    """
    headers = ['Cód.', 'Descripción', 'Cant.', 'P.U.', 'Total']
    data = [headers]
    for f in filas:
        um   = f.get('unidad_medida', '')
        cant = f"{f['cantidad']} {um}".strip()
        data.append([
            Paragraph(str(f.get('cod', '')),          s['desc']),
            Paragraph(str(f.get('descripcion', '')),  s['desc']),
            cant,
            f"Bs. {f['precio_unitario']:.2f}",
            f"Bs. {f['total_item']:.2f}",
        ])

    col_widths = [2.5*cm, 8*cm, 2*cm, 2.8*cm, 2.5*cm]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR',     (0,0), (-1,0),  colors.white),
        ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 8),
        ('ALIGN',         (2,0), (-1,-1), 'CENTER'),
        ('ALIGN',         (3,1), (-1,-1), 'RIGHT'),
        ('ALIGN',         (4,1), (-1,-1), 'RIGHT'),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('GRID',          (0,0), (-1,-1), 0.3, colors.lightgrey),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    return t

# ── Bloque de totales compartido ────────────────────────────────
def _bloque_totales(story, s, total_sin_desc, descuento, iva, total_final):
    """
    Muestra siempre:
        Total s/descuento   Bs. X
        Descuento           Bs. X   (suma de todos los descuentos)
        IVA (13%)           Bs. X   (solo si es factura, iva > 0)
        ─────────────────────────
        TOTAL               Bs. X
    """
    filas = [
        ('Total s/descuento:', f"Bs. {total_sin_desc:.2f}", False),
        ('Descuento:',         f"Bs. {descuento:.2f}",      False),
    ]
    if iva > 0:
        filas.append(('IVA (13%):', f"Bs. {iva:.2f}", False))
    filas.append(('TOTAL:', f"Bs. {total_final:.2f}", True))

    for label, valor, es_ultimo in filas:
        est_l = s['bold_right'] if es_ultimo else s['right']
        est_v = s['bold_right'] if es_ultimo else s['right']
        fila  = Table([[Paragraph(label, est_l), Paragraph(valor, est_v)]],
                      colWidths=[13.5*cm, 3.3*cm])
        fila.setStyle(TableStyle([
            ('TOPPADDING',    (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        if es_ultimo:
            story.append(HRFlowable(width="100%", thickness=1,
                                    color=colors.HexColor('#1a1a2e')))
            story.append(Spacer(1, 4))
        story.append(fila)

# ══════════════════════════════════════════════════════════════
# PDF VENTA
# ══════════════════════════════════════════════════════════════
def exportar_venta_pdf(venta, detalles, cliente_nombre, usuario_nombre, filepath=None):
    if not filepath:
        filepath = os.path.join(os.path.expanduser("~"), "Desktop",
                                f"venta_{venta['id']}.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            topMargin=1.5*cm, bottomMargin=1.5*cm,
                            leftMargin=2*cm,  rightMargin=2*cm)
    s     = _s()
    story = []

    # Encabezado
    story.append(Paragraph(EMPRESA, s['titulo']))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e')))
    story.append(Spacer(1, 8))
    tipo_label = "FACTURA" if venta['tipo_comprobante'] == 'FACTURA' else "NOTA DE VENTA"
    story.append(Paragraph(f"{tipo_label} N° {venta['id']:06d}", s['subtitulo']))
    story.append(Spacer(1, 12))

    fecha = venta['fecha'][:16] if venta.get('fecha') \
            else datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    info  = Table([
        [Paragraph("CLIENTE:",  s['label']), Paragraph(cliente_nombre,  s['bold']),
         Paragraph("FECHA:",    s['label']), Paragraph(fecha,           s['normal'])],
        [Paragraph("VENDEDOR:", s['label']), Paragraph(usuario_nombre,  s['normal']),
         Paragraph("TIPO:",     s['label']), Paragraph(tipo_label,      s['normal'])],
    ], colWidths=[3*cm, 7*cm, 3*cm, 4*cm])
    info.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
                               ('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story.append(info)
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    story.append(Spacer(1, 8))

    # Tabla detalle
    filas = []
    total_sin_desc = 0
    for d in detalles:
        precio_u  = d.get('precio_venta', 0)       # precio sin descuento
        total_item = d.get('total', 0)              # total ya con descuento guardado en BD
        total_sin_desc += d['cantidad'] * precio_u
        filas.append({
            'cod':           d.get('codigo_proveedor') or d.get('codigo_tienda', ''),
            'descripcion':   d['descripcion'],
            'cantidad':      d['cantidad'],
            'unidad_medida': d.get('unidad_medida', ''),
            'precio_unitario': precio_u,
            'total_item':    total_item,
        })
    story.append(_tabla_detalle(filas, s))
    story.append(Spacer(1, 12))

    # Totales
    total_final   = venta.get('total', 0)
    iva           = venta.get('iva', 0)
    descuento_tot = venta.get('descuento_total', 0)
    # Si no viene de BD, calcularlo desde la tabla
    if descuento_tot == 0:
        total_con_desc = sum(d.get('total', 0) for d in detalles)
        descuento_tot  = total_sin_desc - total_con_desc

    _bloque_totales(story, s, total_sin_desc, descuento_tot, iva, total_final)

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Gracias por su compra", s['subtitulo']))

    doc.build(story)
    return filepath


# ══════════════════════════════════════════════════════════════
# PDF COTIZACIÓN
# ══════════════════════════════════════════════════════════════
def exportar_cotizacion_pdf(cotizacion, detalles, cliente_nombre, filepath=None):
    if not filepath:
        filepath = os.path.join(os.path.expanduser("~"), "Desktop",
                                f"cotizacion_{cotizacion['id']}.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            topMargin=1.5*cm, bottomMargin=1.5*cm,
                            leftMargin=2*cm,  rightMargin=2*cm)
    s     = _s()
    story = []

    # Encabezado
    story.append(Paragraph(EMPRESA, s['titulo']))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e')))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"COTIZACIÓN N° {cotizacion['id']:06d}", s['subtitulo']))
    story.append(Spacer(1, 12))

    fecha = cotizacion['fecha'][:16] if cotizacion.get('fecha') else ""
    info  = Table([
        [Paragraph("CLIENTE:", s['label']), Paragraph(cliente_nombre, s['bold']),
         Paragraph("FECHA:",   s['label']), Paragraph(fecha,          s['normal'])],
        [Paragraph("ESTADO:",  s['label']),
         Paragraph(cotizacion.get('estado','ACTIVA'), s['normal']), '', ''],
    ], colWidths=[3*cm, 7*cm, 3*cm, 4*cm])
    info.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
                               ('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story.append(info)
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    story.append(Spacer(1, 8))

    # Tabla detalle
    filas = []
    total_sin_desc = 0
    for d in detalles:
        precio_u   = d.get('precio_venta_original') or d.get('precio', 0)
        total_item = d.get('total', d['cantidad'] * d.get('precio', 0))
        total_sin_desc += d['cantidad'] * precio_u
        filas.append({
            'cod':           d.get('codigo_proveedor') or d.get('codigo_tienda', ''),
            'descripcion':   d['descripcion'],
            'cantidad':      d['cantidad'],
            'unidad_medida': d.get('unidad_medida', ''),
            'precio_unitario': precio_u,
            'total_item':    total_item,
        })
    story.append(_tabla_detalle(filas, s))
    story.append(Spacer(1, 12))

    # Totales
    total_final   = cotizacion.get('total', 0)
    descuento_tot = cotizacion.get('descuento_total', 0)
    if descuento_tot == 0:
        total_con = sum(d.get('total', d['cantidad']*d.get('precio',0)) for d in detalles)
        descuento_tot = total_sin_desc - total_con

    _bloque_totales(story, s, total_sin_desc, descuento_tot, 0, total_final)

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Esta cotización tiene una validez de 15 días.", s['subtitulo']))

    doc.build(story)
    return filepath
