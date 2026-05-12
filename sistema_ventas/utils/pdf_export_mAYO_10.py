from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                 Paragraph, Spacer, HRFlowable, Image,
                                 Frame, PageTemplate, BaseDocTemplate)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import KeepTogether
import os, datetime

# ── Configuración de empresa ────────────────────────────────────
EMPRESA   = "TESLA SRL"
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         '..', 'assets', 'logo.png')

SERVICIOS_TEXT = (
    "<b>ASESORÍA Y SUMINISTRO DE:</b><br/>"
    "— MATERIALES Y EQUIPOS ELÉCTRICOS PARA MEDIA TENSIÓN (MT.) Y (BT.).<br/>"
    "— DISEÑO Y CONSTR. DE PUESTO DE TRANSFORMACIÓN Y SIST. DE DISTRIBUCIÓN.<br/>"
    "— DISEÑO Y CONSTRUCCIÓN DE SISTEMAS ELÉCTRICOS INDUSTRIALES.<br/><br/>"
    "<b>SUMINISTRO DE SERVICIOS EN:</b><br/>"
    "— MANTTO. Y REPARACIÓN DE EQUIPOS ELÉCTRICOS (TRANSFORM., MOTORES, ETC).<br/>"
    "— PRUEBAS, ENSAYOS Y CERTIFICACIONES DE EQUIPOS ELÉCTRICOS"
)

# ── Paleta de colores (azul oscuro como en la proforma) ─────────
AZUL     = colors.HexColor('#1a3a6e')
AZUL_CLR = colors.HexColor('#2e5fa3')
BLANCO   = colors.white
GRIS_F   = colors.HexColor('#f5f5f5')
GRIS_L   = colors.HexColor('#d0d0d0')

# ── Estilos ─────────────────────────────────────────────────────
def _estilos():
    return {
        'titulo':    ParagraphStyle('titulo', fontSize=11, fontName='Helvetica-Bold',
                                    alignment=TA_CENTER, textColor=AZUL, spaceAfter=2),
        'subtitulo': ParagraphStyle('sub',    fontSize=9,  fontName='Helvetica-Bold',
                                    alignment=TA_CENTER, textColor=AZUL),
        'normal':    ParagraphStyle('norm',   fontSize=8,  fontName='Helvetica'),
        'bold':      ParagraphStyle('bold',   fontSize=8,  fontName='Helvetica-Bold'),
        'small':     ParagraphStyle('small',  fontSize=7,  fontName='Helvetica',
                                    textColor=colors.HexColor('#333333'), leading=10),
        'small_b':   ParagraphStyle('smallb', fontSize=7,  fontName='Helvetica-Bold',
                                    textColor=AZUL, leading=11),
        'right':     ParagraphStyle('right',  fontSize=8,  fontName='Helvetica',
                                    alignment=TA_RIGHT),
        'bold_right':ParagraphStyle('br',     fontSize=9,  fontName='Helvetica-Bold',
                                    alignment=TA_RIGHT),
        'label':     ParagraphStyle('label',  fontSize=7,  fontName='Helvetica-Bold',
                                    textColor=AZUL),
        'cell':      ParagraphStyle('cell',   fontSize=7.5,fontName='Helvetica', leading=9),
        'cell_b':    ParagraphStyle('cellb',  fontSize=7.5,fontName='Helvetica-Bold', leading=9),
        'footer':    ParagraphStyle('foot',   fontSize=7,  fontName='Helvetica',
                                    alignment=TA_CENTER, textColor=colors.grey),
    }

# ── Bloque encabezado (logo + servicios + título doc) ───────────
def _encabezado(story, s, titulo_doc):
    """Fila: [LOGO | BLOQUE SERVICIOS]  luego título centrado."""

    # Logo
    logo_cell = ''
    if os.path.exists(LOGO_PATH):
        try:
            img = Image(LOGO_PATH, width=3.5*cm, height=3*cm)
            logo_cell = img
        except:
            logo_cell = Paragraph(EMPRESA, s['titulo'])
    else:
        logo_cell = Paragraph(EMPRESA, s['titulo'])

    servicios = Paragraph(SERVICIOS_TEXT, s['small'])

    header_table = Table(
        [[logo_cell, servicios]],
        colWidths=[4*cm, 13.8*cm]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING',  (1,0), (1,0),   6),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING',   (0,0), (-1,-1), 0),
        ('BOTTOMPADDING',(0,0), (-1,-1), 4),
        ('BOX',          (1,0), (1,0),   0.5, AZUL),
        ('BACKGROUND',   (1,0), (1,0),   colors.HexColor('#eef2f9')),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=AZUL))
    story.append(Spacer(1, 5))
    story.append(Paragraph(titulo_doc, s['titulo']))
    story.append(Spacer(1, 5))

# ── Bloque datos del cliente ─────────────────────────────────────
def _datos_cliente(story, s, nombre, direccion, telefono, ci_nit,fecha_str):
    """Bloque sin bordes + título centrado"""

    # 🔹 TÍTULO CENTRADO
    story.append(Paragraph(
        "<b>DATOS GENERALES DEL CLIENTE</b>",
        ParagraphStyle('tcliente',
            fontSize=9,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            textColor=AZUL
        )
    ))
    story.append(Spacer(1, 6))

    nombre    = nombre or ''
    direccion = direccion or ''
    telefono  = telefono or ''

    data = [[
        Paragraph('<b>CLIENTE:</b>', s['label']),
        Paragraph(nombre, s['cell']),
        Paragraph('<b>DIRECCIÓN:</b>', s['label']),
        Paragraph(direccion, s['cell']),
        Paragraph('<b>TEL:</b>', s['label']),
        Paragraph(telefono, s['cell']),
    ],[
        Paragraph('<b>CI/NIT:</b>', s['label']),
        Paragraph(ci_nit, s['cell']),
        '', '', # columnas vacías para mantener estructura
        Paragraph('<b>FECHA:</b>', s['label']),
        Paragraph(fecha_str, s['cell']),
    ]]

    t = Table(data, colWidths=[1.5*cm, 4.5*cm, 2*cm, 4*cm, 1.5*cm, 4.3*cm])

    # 🔥 SIN BORDES (esto es lo importante)
    t.setStyle(TableStyle([
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING',    (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING',   (0,0), (-1,-1), 3),

        # ❌ Eliminamos líneas
        ('BOX', (0,0), (-1,-1), 0, colors.white),
        ('INNERGRID', (0,0), (-1,-1), 0, colors.white),
    ]))

    story.append(t)
    story.append(Spacer(1, 8))

# ── Tabla de detalle principal ───────────────────────────────────
def _tabla_detalle(s, filas):
    """
    filas: list of dicts:
        item, cantidad, unidad, descripcion, marca, precio_unit, precio_total
    Columnas: ITEM | CANT. | UNID. | DESCRIPCIÓN | MARCA | P/UNIT.(Bs.) | P/TOTAL(Bs.)
    """
    headers = ['ITEM', 'CANT.', 'UNID.', 'DESCRIPCIÓN', 'MARCA',
               'P/UNIT. (Bs.)', 'P/TOTAL (Bs.)']

    # Estilo encabezado
    hdr_style = [Paragraph(h, ParagraphStyle('hh', fontSize=7.5,
                  fontName='Helvetica-Bold', textColor=BLANCO,
                  alignment=TA_CENTER)) for h in headers]
    data = [hdr_style]

    for f in filas:
        data.append([
            Paragraph(str(f['item']),       s['cell']),
            Paragraph(str(f['cantidad']),   s['cell']),
            Paragraph(str(f['unidad']),     s['cell']),
            Paragraph(str(f['descripcion']),s['cell']),
            Paragraph(str(f['marca']),      s['cell']),
            Paragraph(f"{f['precio_unit']:.2f}", ParagraphStyle('cr', fontSize=7.5,
                      fontName='Helvetica', alignment=TA_RIGHT)),
            Paragraph(f"{f['precio_total']:.2f}", ParagraphStyle('cr2', fontSize=7.5,
                      fontName='Helvetica', alignment=TA_RIGHT)),
        ])

    col_widths = [1*cm, 1.5*cm, 1.5*cm, 6.5*cm, 2.5*cm, 2.5*cm, 2.3*cm]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND',    (0,0), (-1,0),  AZUL),
        ('TEXTCOLOR',     (0,0), (-1,0),  BLANCO),
        ('ALIGN',         (0,0), (-1,0),  'CENTER'),
        # Datos
        ('FONTSIZE',      (0,0), (-1,-1), 7.5),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('ALIGN',         (0,1), (2,-1),  'CENTER'),   # ITEM, CANT, UNID
        ('ALIGN',         (5,1), (-1,-1), 'RIGHT'),    # precios
        # Filas alternas
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [BLANCO, GRIS_F]),
        # Bordes
        ('GRID',          (0,0), (-1,-1), 0.4, GRIS_L),
        ('LINEBELOW',     (0,0), (-1,0),  1,   AZUL),
        # Padding
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING',   (0,0), (-1,-1), 3),
        ('RIGHTPADDING',  (0,0), (-1,-1), 3),
    ]))
    return t

# ── Bloque de totales ────────────────────────────────────────────
def _bloque_totales(s, total_sin_desc, descuento, iva, total_final):
    filas = [
        ('SUB TOTAL:', f"Bs.  {total_sin_desc:,.2f}"),
    ]
    if iva > 0:
        filas.append(('IVA (13%):', f"Bs.  {iva:,.2f}"))
    filas.append(('DESCUENTO:', f"Bs.  {descuento:,.2f}"))
    filas.append(('TOTAL:', f"Bs.  {total_final:,.2f}"))

    data = []
    for label, valor in filas:
        es_total = label == 'TOTAL:'
        fs = 8.5 if es_total else 8
        fn = 'Helvetica-Bold' if es_total else 'Helvetica'
        data.append([
            '',   # columna vacía izquierda (ocupa espacio)
            Paragraph(label, ParagraphStyle('tl', fontSize=fs, fontName=fn,
                              alignment=TA_RIGHT, textColor=AZUL if es_total else colors.black)),
            Paragraph(valor,  ParagraphStyle('tv', fontSize=fs, fontName=fn,
                              alignment=TA_RIGHT, textColor=AZUL if es_total else colors.black)),
        ])

    t = Table(data, colWidths=[9.5*cm, 4*cm, 4.3*cm])
    t.setStyle(TableStyle([
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LINEABOVE',     (1,-1), (-1,-1), 1, AZUL),   # línea sobre TOTAL
        ('BACKGROUND',    (1,-1), (-1,-1), colors.HexColor('#eef2f9')),
    ]))
    return t

# ── Callback número de página ────────────────────────────────────
def _add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(colors.grey)
    page_num = canvas.getPageNumber()
    total    = doc._pageCount if hasattr(doc, '_pageCount') else '?'
    canvas.drawRightString(
        A4[0] - 1.5*cm, 1*cm,
        f"Pág. {page_num}")
    canvas.restoreState()

# ══════════════════════════════════════════════════════════════════
# Clase doc con conteo de páginas
# ══════════════════════════════════════════════════════════════════
class _DocConPaginas(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        self._pageCount = 0
        super().__init__(*args, **kwargs)

    def handle_pageEnd(self):
        self._pageCount += 1
        super().handle_pageEnd()

# ══════════════════════════════════════════════════════════════════
# PDF VENTA
# ══════════════════════════════════════════════════════════════════
def exportar_venta_pdf(venta, detalles, cliente_nombre, usuario_nombre,
                       cliente_direccion='', cliente_telefono='', cliente_ci_nit='', filepath=None):
    if not filepath:
        fecha_str = (venta.get('fecha','')[:10] or
                     datetime.date.today().isoformat()).replace('-','')
        nombre_f  = (cliente_nombre or 'cliente').replace(' ','_')
        nombre_arc= f"venta_{nombre_f}_{fecha_str}_{venta['id']:04d}.pdf"
        filepath  = os.path.join(os.path.expanduser("~"), "Desktop", nombre_arc)

    doc = _DocConPaginas(filepath, pagesize=A4,
                         topMargin=1.5*cm, bottomMargin=1.8*cm,
                         leftMargin=1.5*cm, rightMargin=1.5*cm)
    s     = _estilos()
    story = []

    # Encabezado
    tipo_label = ("FACTURA" if venta['tipo_comprobante'] == 'FACTURA'
                  else "NOTA DE VENTA")
    _encabezado(story, s,
                f"NOTA DE VENTA:  ÍTEM DE SUMINISTRO DE MATERIALES ELÉCTRICOS")

    # Datos cliente
    fecha_doc = (venta.get('fecha','')[:10] or
                 datetime.date.today().isoformat())
    _datos_cliente(story, s, cliente_nombre, cliente_direccion,
                   cliente_telefono, venta.get('ci_nit', ''), fecha_doc)

    # Referencia
    story.append(Paragraph(
        f"<b>N° {venta['id']:06d}  |  {tipo_label}</b>", s['subtitulo']))
    story.append(Spacer(1, 6))

    # Tabla detalle
    filas = []
    for i, d in enumerate(detalles, 1):
        filas.append({
            'item':        i,
            'cantidad':    d['cantidad'],
            'unidad':      d.get('unidad_medida',''),
            'descripcion': d['descripcion'],
            'marca':       d.get('marca',''),
            'precio_unit': d.get('precio_venta', 0),           # sin descuento
            'precio_total':d['cantidad'] * d.get('precio_venta', 0),  # sin desc
        })
    story.append(_tabla_detalle(s, filas))
    story.append(Spacer(1, 8))

    # Totales
    total_sin = venta.get('subtotal', 0)
    descuento = venta.get('descuento_total', 0)
    iva       = venta.get('iva', 0)
    total_fin = venta.get('total', 0)
    story.append(_bloque_totales(s, total_sin, descuento, iva, total_fin))

    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRIS_L))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Gracias por su preferencia.", s['footer']))

    doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
    return filepath


# ══════════════════════════════════════════════════════════════════
# PDF COTIZACIÓN
# ══════════════════════════════════════════════════════════════════
def exportar_cotizacion_pdf(cotizacion, detalles, cliente_nombre,
                             cliente_direccion='', cliente_telefono='',
                             cliente_ci_nit='',
                             filepath=None):
    if not filepath:
        fecha_str = (cotizacion.get('fecha','')[:10] or
                     datetime.date.today().isoformat()).replace('-','')
        nombre_f  = (cliente_nombre or 'cliente').replace(' ','_')
        nombre_arc= f"cotizacion_{nombre_f}_{fecha_str}_{cotizacion['id']:04d}.pdf"
        filepath  = os.path.join(os.path.expanduser("~"), "Desktop", nombre_arc)

    doc = _DocConPaginas(filepath, pagesize=A4,
                         topMargin=1.5*cm, bottomMargin=1.8*cm,
                         leftMargin=1.5*cm, rightMargin=1.5*cm)
    s     = _estilos()
    story = []

    titulo = """
    <u>PROFORMA</u>: ÍTEM DE SUMINISTRO DE MATERIALES ELÉCTRICOS PARA BAJA TENSIÓN (B.T.)
    """

    _encabezado(story, s, titulo)

    # Encabezado
    # _encabezado(story, s,
    #             "PROFORMA:  ÍTEM DE SUMINISTRO DE MATERIALES ELÉCTRICOS")

    # Datos cliente
    fecha_doc = (cotizacion.get('fecha','')[:10] or
                 datetime.date.today().isoformat())
    _datos_cliente(story, s, cliente_nombre, cliente_direccion,
               cliente_telefono, cliente_ci_nit, fecha_doc)

    # Referencia
    story.append(Paragraph(
        f"<b>COTIZACIÓN N° {cotizacion['id']:06d}</b>  "
        f"| Estado: {cotizacion.get('estado','ACTIVA')}", s['subtitulo']))
    story.append(Spacer(1, 6))

    # Tabla detalle
    filas = []
    for i, d in enumerate(detalles, 1):
        precio_u = d.get('precio_venta_original') or d.get('precio', 0)
        filas.append({
            'item':        i,
            'cantidad':    d['cantidad'],
            'unidad':      d.get('unidad_medida',''),
            'descripcion': d['descripcion'],
            'marca':       d.get('marca',''),
            'precio_unit': precio_u,
            'precio_total':d['cantidad'] * precio_u,
        })
    story.append(_tabla_detalle(s, filas))
    story.append(Spacer(1, 8))

    # Totales
    total_sin = cotizacion.get('subtotal', cotizacion.get('total', 0))
    descuento = cotizacion.get('descuento_total', 0)
    total_fin = cotizacion.get('total', 0)

    # Si subtotal no está guardado, calcularlo de los detalles
    if total_sin == total_fin and descuento == 0:
        total_sin = sum(d['cantidad'] * (d.get('precio_venta_original') or d.get('precio',0))
                       for d in detalles)
        descuento = total_sin - total_fin

    story.append(_bloque_totales(s, total_sin, descuento, 0, total_fin))

    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRIS_L))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "⚠  La presente cotización tiene una validez de <b>2 días</b> a partir de la fecha de emisión.",
        s['footer']))

    doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
    return filepath
