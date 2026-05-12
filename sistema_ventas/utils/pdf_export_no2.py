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
    "<b>ASESORIA Y SUMINISTRO DE:</b><br/>"
    "MATERIALES Y EQUIPOS ELÉCTRICOS PARA MEDIA TENSIÓN (MT.) Y (BT.).<br/>"
    "DISEÑO Y CONSTR. DE PUESTO DE TRANSFORMACIÓN Y SIST. DE DISTRIBUCIÓN.<br/>"
    "DISEÑO Y CONSTRUCIÓN DE SISTEMAS ELÉCTRICOS INDUSTRIALES.<br/><br/>"
    "<b>SUMINISTRO DE SERVICIOS EN:</b><br/>"
    "MANTTO. Y REPARACIÓN DE EQUIPOS ELÉCTRICOS (TRANSFORM., MOTORES, ETC).<br/>"
    "PRUEBAS, ENSAYOS Y CERTIFICACIONES DE EQUIPOS ELÉCTRICOS"
)

# ── Paleta de colores ────────────────────────────────────────────
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
        'label':     ParagraphStyle('label',  fontSize=7.5, fontName='Helvetica-Bold',
                                    textColor=AZUL),
        'cell':      ParagraphStyle('cell',   fontSize=8, fontName='Helvetica', leading=10),
        'cell_b':    ParagraphStyle('cellb',  fontSize=8, fontName='Helvetica-Bold', leading=10),
        'footer':    ParagraphStyle('foot',   fontSize=7,  fontName='Helvetica',
                                    alignment=TA_CENTER, textColor=colors.grey),
    }

# ── Bloque encabezado (logo + servicios + título doc) ───────────
def _encabezado(story, s, titulo_doc):
    # LOGO
    if os.path.exists(LOGO_PATH):
        logo = Image(LOGO_PATH, width=2.5*cm, height=2*cm)
    else:
        logo = Paragraph(EMPRESA, s['titulo'])

    servicios = Paragraph(SERVICIOS_TEXT, s['small'])

    t = Table([[logo, servicios]], colWidths=[3*cm, 14.8*cm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (1,0), (1,0), 6),
    ]))

    story.append(t)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    story.append(Spacer(1, 4))

    # Título principal (PROFORMA)
    story.append(Paragraph(titulo_doc, s['titulo']))
    story.append(Spacer(1, 8))

# ── DATOS CLIENTE (formato igual al PDF) ──────────────────────────────
def _datos_cliente(story, s, nombre, direccion, telefono, fecha_str):
    # Formato: CLIENTE: nombre    DIRECCION: direccion    TEL: telefono
    #          FECHA: fecha
    
    data = [[
        Paragraph('<b>CLIENTE:</b>', s['label']),
        Paragraph(nombre or '', s['cell']),
        Paragraph('<b>DIRECCION:</b>', s['label']),
        Paragraph(direccion or '', s['cell']),
        Paragraph('<b>TEL:</b>', s['label']),
        Paragraph(telefono or '', s['cell']),
        Paragraph('<b>FECHA:</b>', s['label']),
        Paragraph(fecha_str, s['cell']),
    ]]

    t = Table(data, colWidths=[1.8*cm, 3.5*cm, 2.2*cm, 3.5*cm, 1.2*cm, 2.5*cm, 1.5*cm, 3*cm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))

    story.append(t)
    story.append(Spacer(1, 6))

# ── Tabla de detalle principal (igual al PDF) ───────────────────────────────────
def _tabla_detalle(s, filas):
    """
    Columnas: ITEM | CANT. | UNID. | DESCRIPCION | MARCA | P/UNIT. (Bs.) | P/TOTAL (Bs.)
    """
    headers = ['ITEM', 'CANT.', 'UNID.', 'DESCRIPCION', 'MARCA',
               'P/UNIT. (Bs.)', 'P/TOTAL (Bs.)']

    # Estilo encabezado
    hdr_style = [Paragraph(h, ParagraphStyle('hh', fontSize=9,
                  fontName='Helvetica-Bold', textColor=BLANCO,
                  alignment=TA_CENTER)) for h in headers]
    data = [hdr_style]

    for f in filas:
        data.append([
            Paragraph(str(f['item']),       s['cell']),
            Paragraph(f"{f['cantidad']:,.2f}".replace('.00','') if f['cantidad'] == int(f['cantidad']) else f"{f['cantidad']:,.2f}", s['cell']),
            Paragraph(str(f['unidad']),     s['cell']),
            Paragraph(str(f['descripcion']),s['cell']),
            Paragraph(str(f['marca']),      s['cell']),
            Paragraph(f"{f['precio_unit']:,.2f}", ParagraphStyle('cr', fontSize=8,
                      fontName='Helvetica', alignment=TA_RIGHT)),
            Paragraph(f"{f['precio_total']:,.2f}", ParagraphStyle('cr2', fontSize=8,
                      fontName='Helvetica', alignment=TA_RIGHT)),
        ])

    col_widths = [1.2*cm, 1.8*cm, 1.5*cm, 6*cm, 2.5*cm, 2.5*cm, 2.5*cm]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND',    (0,0), (-1,0),  AZUL),
        ('TEXTCOLOR',     (0,0), (-1,0),  BLANCO),
        ('ALIGN',         (0,0), (-1,0),  'CENTER'),
        ('FONTSIZE',      (0,0), (-1,0),  9),
        # Datos
        ('FONTSIZE',      (0,1), (-1,-1), 8),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN',         (0,1), (2,-1),  'CENTER'),   # ITEM, CANT, UNID
        ('ALIGN',         (5,1), (-1,-1), 'RIGHT'),    # precios
        # Filas alternas
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [BLANCO, GRIS_F]),
        # Bordes
        ('GRID',          (0,0), (-1,-1), 0.5, GRIS_L),
        ('LINEBELOW',     (0,0), (-1,0),  1.5, AZUL),
        # Padding
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 4),
        ('RIGHTPADDING',  (0,0), (-1,-1), 4),
    ]))
    return t

# ── Bloque de totales (igual al PDF) ────────────────────────────────────────
def _bloque_totales(s, total_sin, descuento, iva, total_final):
    # El PDF muestra: SUB TOTAL: Bs. 54,942.45 en una sola línea sin tabla adicional
    
    total_text = f"<b>SUB TOTAL: Bs. {total_sin:,.2f}</b>"
    
    story = []
    story.append(Spacer(1, 8))
    story.append(Paragraph(total_text, ParagraphStyle('total', fontSize=10, fontName='Helvetica-Bold',
                              alignment=TA_RIGHT, textColor=AZUL)))
    
    if iva > 0:
        story.append(Paragraph(f"IVA (13%): Bs. {iva:,.2f}", ParagraphStyle('iva', fontSize=9,
                              fontName='Helvetica', alignment=TA_RIGHT)))
    
    if descuento > 0:
        story.append(Paragraph(f"DESCUENTO: Bs. {descuento:,.2f}", ParagraphStyle('desc', fontSize=9,
                              fontName='Helvetica', alignment=TA_RIGHT)))
    
    if total_final != total_sin:
        story.append(Paragraph(f"<b>TOTAL: Bs. {total_final:,.2f}</b>", ParagraphStyle('total_final', 
                              fontSize=10, fontName='Helvetica-Bold', alignment=TA_RIGHT, 
                              textColor=AZUL)))
    
    return story

# ── Callback número de página ────────────────────────────────────
def _add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(colors.grey)
    page_num = canvas.getPageNumber()
    canvas.drawRightString(
        A4[0] - 1.5*cm, 1*cm,
        f"Pag. {page_num}")
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
# PDF PROFORMA/COTIZACIÓN (igual al PDF que me mostraste)
# ══════════════════════════════════════════════════════════════════
def exportar_cotizacion_pdf(cotizacion, detalles, cliente_nombre,
                             cliente_direccion='', cliente_telefono='',
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

    # Encabezado (igual al PDF)
    _encabezado(story, s,
                "PROFORMA: ITEM DE SUMINISTRO DE MATERIALES ELECTRICOS PARA BAJA TENSION (B.T.)")

    # Datos cliente (formato igual al PDF)
    fecha_doc = (cotizacion.get('fecha','')[:10] or
                 datetime.date.today().isoformat())
    # Formatear fecha como "LPZ / 17 / ABRIL / 2026"
    try:
        fecha_obj = datetime.datetime.strptime(fecha_doc, '%Y-%m-%d')
        fecha_formateada = f"LPZ / {fecha_obj.day:02d} / {fecha_obj.strftime('%B').upper()} / {fecha_obj.year}"
    except:
        fecha_formateada = f"LPZ / {fecha_doc}"
    
    _datos_cliente(story, s, cliente_nombre, cliente_direccion,
                   cliente_telefono, fecha_formateada)

    # Tabla detalle
    filas = []
    for i, d in enumerate(detalles, 1):
        precio_u = d.get('precio_venta_original') or d.get('precio', 0)
        filas.append({
            'item':        i,
            'cantidad':    d['cantidad'],
            'unidad':      d.get('unidad_medida', ''),
            'descripcion': d['descripcion'],
            'marca':       d.get('marca', ''),
            'precio_unit': precio_u,
            'precio_total': d['cantidad'] * precio_u,
        })
    story.append(_tabla_detalle(s, filas))

    # Totales
    total_sin = cotizacion.get('subtotal', 0)
    if total_sin == 0:
        total_sin = sum(d['cantidad'] * (d.get('precio_venta_original') or d.get('precio',0))
                       for d in detalles)
    
    descuento = cotizacion.get('descuento_total', 0)
    iva = cotizacion.get('iva', 0)
    total_fin = cotizacion.get('total', total_sin)
    
    story.extend(_bloque_totales(s, total_sin, descuento, iva, total_fin))

    doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
    return filepath


# ══════════════════════════════════════════════════════════════════
# Función para crear una proforma de ejemplo (como la del PDF)
# ══════════════════════════════════════════════════════════════════
def exportar_proforma_ejemplo(filepath=None):
    """Genera una proforma exactamente igual al PDF que mostraste"""
    
    detalles = [
        {
            'cantidad': 2000.00,
            'unidad_medida': 'Mts.',
            'descripcion': 'CABLE FLEX. ECOLOGICO AFITOX 750 V. 1x2.5 mm2 NEGRO',
            'marca': 'NEXANS',
            'precio': 4.89,
            'precio_venta_original': 4.89
        },
        {
            'cantidad': 3000.00,
            'unidad_medida': 'Mts.',
            'descripcion': 'CABLE FLEX. INDUSC DUFLEX 750 V. 1X6 mm2',
            'marca': 'INDUSCABOS',
            'precio': 11.90,
            'precio_venta_original': 11.90
        },
        {
            'cantidad': 5.00,
            'unidad_medida': 'rollo',
            'descripcion': 'CABLE FLEX. INDUSC DUFLEX 1x 10 mm2',
            'marca': 'INDUSCABOS',
            'precio': 1892.49,
            'precio_venta_original': 1892.49
        }
    ]
    
    cotizacion = {
        'id': 1,
        'fecha': '2026-04-17',
        'subtotal': 54942.45,
        'descuento_total': 0,
        'iva': 0,
        'total': 54942.45,
        'estado': 'ACTIVA'
    }
    
    return exportar_cotizacion_pdf(
        cotizacion=cotizacion,
        detalles=detalles,
        cliente_nombre='',
        cliente_direccion='LA PAZ',
        cliente_telefono='',
        filepath=filepath
    )


# Ejemplo de uso:
if __name__ == "__main__":
    # Genera el PDF exactamente igual al que me mostraste
    exportar_proforma_ejemplo()