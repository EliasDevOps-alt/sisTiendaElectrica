import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox, ttk
from views.base_view import *
from views.carrito_widget import CarritoWidget
from controllers.controller import *
from utils.pdf_export import exportar_venta_pdf
import os, subprocess, sys

# ═══════════════════════════════════════════════════════════════
#  LÓGICA DE DESCUENTOS
#  - precio_compra   → costo base
#  - porcentaje_venta → margen total  (ej: 20%)
#  - descuento_maximo → piso reservado (ej: 5%)
#  - margen negociable = porcentaje_venta - descuento_maximo  (ej: 15%)
#  - si usuario aplica X% de descuento:
#       reduccion = margen_negociable * (X/100)
#       nuevo_margen = porcentaje_venta - reduccion
#       precio_final = precio_compra * (1 + nuevo_margen/100)
# ═══════════════════════════════════════════════════════════════

def calcular_precio_con_descuento(producto, pct_descuento_sobre_margen):
    """
    pct_descuento_sobre_margen: 0-100  (ej: 50 → aplica 50% del margen negociable)
    Retorna (precio_final, descuento_bs, precio_sin_desc)
    """
    costo          = producto['precio_compra']
    margen_total   = producto['porcentaje_venta']       # ej: 20
    piso           = producto['descuento_maximo']        # ej: 5  (reserva)
    margen_negoc   = max(margen_total - piso, 0)         # ej: 15

    reduccion      = margen_negoc * (pct_descuento_sobre_margen / 100.0)  # ej: 7.5
    nuevo_margen   = margen_total - reduccion                               # ej: 12.5
    precio_final   = round(costo * (1 + nuevo_margen / 100.0), 2)
    precio_sin_desc= producto['precio_venta']            # precio original sin desc
    descuento_bs   = round(precio_sin_desc - precio_final, 2)
    return precio_final, descuento_bs, precio_sin_desc


# ── Helpers de diálogo ──────────────────────────────────────────
def _pedir_precio(parent, descripcion):
    """Dialogo modal para ingresar precio cuando el producto no tiene precio."""
    top = tk.Toplevel(parent)
    top.title("Precio requerido")
    top.resizable(False, False)
    top.grab_set()
    top.configure(bg='white')
    w, h = 380, 230
    sw, sh = top.winfo_screenwidth(), top.winfo_screenheight()
    top.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    hdr = tk.Frame(top, bg='#e65100', padx=16, pady=10)
    hdr.pack(fill='x')
    tk.Label(hdr, text="⚠️  Producto sin precio",
             font=("Arial", 11, "bold"), bg='#e65100', fg='white').pack(anchor='w')

    body = tk.Frame(top, bg='white', padx=20, pady=14)
    body.pack(fill='both', expand=True)
    tk.Label(body, text=f"Producto:  {descripcion[:50]}",
             font=("Arial", 9), bg='white', fg='#333',
             wraplength=330, justify='left').pack(anchor='w')
    tk.Label(body, text="Este producto no tiene precio asignado.",
             font=("Arial", 8), bg='white', fg='#888').pack(anchor='w', pady=(2,10))
    tk.Label(body, text="Ingrese el precio para esta venta (Bs.):",
             font=("Arial", 9, "bold"), bg='white').pack(anchor='w')

    precio_var = tk.StringVar(value='')
    import ttkbootstrap as _tb
    entry = _tb.Entry(body, textvariable=precio_var, width=20,
                      font=("Arial", 11), bootstyle="warning")
    entry.pack(anchor='w', pady=4, ipady=4)
    entry.focus()

    resultado = [None]

    def confirmar():
        try:
            v = float(precio_var.get())
            if v <= 0: raise ValueError
            resultado[0] = v
            top.destroy()
        except:
            tk.Label(body, text="Ingrese un precio válido mayor a 0",
                     fg='red', bg='white', font=("Arial",8)).pack(anchor='w')

    btn_row = tk.Frame(body, bg='white')
    btn_row.pack(anchor='e', pady=(8,0))
    _tb.Button(btn_row, text="Cancelar", bootstyle="secondary-outline",
               command=top.destroy).pack(side='left', padx=(0,6))
    _tb.Button(btn_row, text="✅ Confirmar", bootstyle="warning",
               command=confirmar).pack(side='left')
    entry.bind("<Return>", lambda e: confirmar())

    top.wait_window()
    return resultado[0]


def _pedir_descripcion(parent, descripcion_actual):
    """Dialogo para editar la descripción de un ítem del carrito."""
    top = tk.Toplevel(parent)
    top.title("Editar descripción")
    top.resizable(False, False)
    top.grab_set()
    top.configure(bg='white')
    w, h = 420, 200
    sw, sh = top.winfo_screenwidth(), top.winfo_screenheight()
    top.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    hdr = tk.Frame(top, bg=HEADER_BG, padx=16, pady=10)
    hdr.pack(fill='x')
    tk.Label(hdr, text="✏️  Editar descripción del ítem",
             font=("Arial", 11, "bold"), bg=HEADER_BG, fg='white').pack(anchor='w')

    body = tk.Frame(top, bg='white', padx=20, pady=14)
    body.pack(fill='both', expand=True)
    tk.Label(body, text="Descripción para esta venta/cotización:",
             font=("Arial", 9, "bold"), bg='white').pack(anchor='w')

    desc_var = tk.StringVar(value=descripcion_actual)
    import ttkbootstrap as _tb
    entry = _tb.Entry(body, textvariable=desc_var, width=45,
                      font=("Arial", 10), bootstyle="primary")
    entry.pack(fill='x', pady=6, ipady=4)
    entry.select_range(0, 'end')
    entry.focus()

    resultado = [None]

    def confirmar():
        v = desc_var.get().strip()
        if v:
            resultado[0] = v
            top.destroy()

    btn_row = tk.Frame(body, bg='white')
    btn_row.pack(anchor='e')
    _tb.Button(btn_row, text="Cancelar", bootstyle="secondary-outline",
               command=top.destroy).pack(side='left', padx=(0,6))
    _tb.Button(btn_row, text="✅ Aplicar", bootstyle="dark",
               command=confirmar).pack(side='left')
    entry.bind("<Return>", lambda e: confirmar())

    top.wait_window()
    return resultado[0]


def _editar_item_dialog(parent, item, callback):
    """
    Diálogo para editar Cantidad, Precio unitario, Descripción,
    Unidad de Medida y Marca de un ítem del carrito.
    Recalcula totales al aceptar. No modifica la BD.
    """
    top = tk.Toplevel(parent)
    top.title("Editar ítem del carrito")
    top.resizable(False, False)
    top.grab_set()
    top.configure(bg='white')
    w, h = 500, 500
    sw, sh = top.winfo_screenwidth(), top.winfo_screenheight()
    top.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    hdr = tk.Frame(top, bg=HEADER_BG, padx=16, pady=10)
    hdr.pack(fill='x')
    tk.Label(hdr, text="✏️  Editar ítem — solo para esta venta/cotización",
             font=("Arial", 10, "bold"), bg=HEADER_BG, fg='white').pack(anchor='w')
    tk.Label(hdr, text="No modifica el producto en la base de datos",
             font=("Arial", 7), bg=HEADER_BG, fg='#aaa').pack(anchor='w')

    body = tk.Frame(top, bg='white', padx=20, pady=12)
    body.pack(fill='both', expand=True)
    body.columnconfigure(1, weight=1)

    cant_var  = tk.StringVar(value=str(item.get('cantidad', 1)))
    precio_var= tk.StringVar(value=str(item.get('precio_venta_original', 0)))
    desc_var  = tk.StringVar(value=item.get('descripcion_venta') or item.get('descripcion',''))
    um_var    = tk.StringVar(value=item.get('unidad_medida',''))
    marca_var = tk.StringVar(value=item.get('marca_venta') or item.get('marca',''))

    # Preview del total
    preview_var = tk.StringVar()

    def _update_preview(*_):
        try:
            c = int(cant_var.get())
            p = float(precio_var.get())
            preview_var.set(f"Total s/desc: Bs. {c*p:.2f}")
        except:
            preview_var.set("Total s/desc: —")

    cant_var.trace('w',   _update_preview)
    precio_var.trace('w', _update_preview)

    sep_style = {'font':("Arial", 8, "bold"), 'bg':'white',
                 'fg':HEADER_BG, 'anchor':'w'}

    # ── Bloque cantidad / precio ──────────────────────────────
    tk.Label(body, text="CANTIDAD Y PRECIO", **sep_style).grid(
        row=0, column=0, columnspan=2, sticky='w', pady=(0,4))
    tk.Frame(body, bg='#eee', height=1).grid(
        row=1, column=0, columnspan=2, sticky='ew', pady=(0,8))

    campos_num = [
        ("Cantidad *:",      cant_var,   "int"),
        ("Precio unit. *:",  precio_var, "float"),
    ]
    entries = []
    for r, (lbl, var, _) in enumerate(campos_num, start=2):
        tk.Label(body, text=lbl, font=("Arial", 9, "bold"),
                 bg='white', fg='#555').grid(row=r, column=0, sticky='w',
                 padx=(0,8), pady=5)
        e = tb.Entry(body, textvariable=var, width=18,
                     font=("Arial", 10), bootstyle="warning")
        e.grid(row=r, column=1, sticky='w', pady=5, ipady=3)
        entries.append(e)

    # Preview total
    tk.Label(body, textvariable=preview_var,
             font=("Arial", 8, "italic"), bg='white',
             fg='#e65100').grid(row=4, column=1, sticky='w', pady=(0,8))

    # ── Bloque descripción / UM / marca ───────────────────────
    tk.Label(body, text="DESCRIPCIÓN / PRESENTACIÓN", **sep_style).grid(
        row=5, column=0, columnspan=2, sticky='w', pady=(4,4))
    tk.Frame(body, bg='#eee', height=1).grid(
        row=6, column=0, columnspan=2, sticky='ew', pady=(0,8))

    campos_txt = [
        ("Descripción:",  desc_var),
        ("Unidad Med.:",  um_var),
        ("Marca:",        marca_var),
    ]
    for r, (lbl, var) in enumerate(campos_txt, start=7):
        tk.Label(body, text=lbl, font=("Arial", 9, "bold"),
                 bg='white', fg='#555').grid(row=r, column=0, sticky='w',
                 padx=(0,8), pady=5)
        e = tb.Entry(body, textvariable=var, font=("Arial", 10),
                     bootstyle="primary")
        e.grid(row=r, column=1, sticky='ew', pady=5, ipady=3)
        entries.append(e)

    entries[0].focus()
    _update_preview()

    error_lbl = tk.Label(body, text='', font=("Arial", 8),
                         bg='white', fg='red')
    error_lbl.grid(row=10, column=0, columnspan=2, sticky='w')

    def aplicar():
        # Validar cantidad y precio
        try:
            nueva_cant = int(cant_var.get())
            if nueva_cant <= 0: raise ValueError
        except:
            error_lbl.config(text="La cantidad debe ser un número entero mayor a 0")
            return
        try:
            nuevo_precio = float(precio_var.get())
            if nuevo_precio <= 0: raise ValueError
        except:
            error_lbl.config(text="El precio debe ser un número mayor a 0")
            return

        # Actualizar cantidad
        item['cantidad'] = nueva_cant

        # Actualizar precio — recalcular precio_final manteniendo el % de descuento
        item['precio_venta_original'] = nuevo_precio
        item['precio_venta']          = nuevo_precio
        pct = item.get('pct_descuento', 0)
        # Recalcular con la misma lógica de margen negociable
        # Si no hay precio_compra real (producto sin precio), usar precio directo
        pc = item.get('precio_compra', 0)
        pv_orig = item.get('porcentaje_venta', 0)
        piso    = item.get('descuento_maximo', 0)
        if pc > 0 and pv_orig > 0:
            margen_negoc = max(pv_orig - piso, 0)
            reduccion    = margen_negoc * (pct / 100.0)
            nuevo_margen = pv_orig - reduccion
            precio_final = round(pc * (1 + nuevo_margen / 100.0), 2)
        else:
            # Precio manual: aplicar descuento directo sobre el precio ingresado
            precio_final = round(nuevo_precio * (1 - pct / 100.0), 2)
        item['precio_final']  = precio_final
        item['descuento_bs']  = round(nuevo_precio - precio_final, 2)

        # Actualizar texto / presentación
        item['descripcion_venta'] = desc_var.get().strip() or item.get('descripcion','')
        item['unidad_medida']     = um_var.get().strip()
        item['marca_venta']       = marca_var.get().strip()

        callback()
        top.destroy()

    btn_frame = tk.Frame(top, bg='white', pady=8)
    btn_frame.pack(fill='x', padx=20)
    tb.Button(btn_frame, text="Cancelar", bootstyle="secondary-outline",
              command=top.destroy).pack(side='right', padx=(6,0))
    tb.Button(btn_frame, text="✅ Aplicar y recalcular",
              bootstyle="dark", command=aplicar).pack(side='right')
    top.bind("<Return>", lambda e: aplicar())


# ═══════════════════════════════════════════════════════════════
class VentasView(tk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent, bg=CONTENT_BG)
        self.usuario = usuario
        self._build()
        self._load_historial()

    def _build(self):
        make_page_header(self, "🛒 Ventas", "Registrar nueva venta y consultar historial").pack(fill=X)
        notebook = tb.Notebook(self, bootstyle="dark")
        notebook.pack(fill=BOTH, expand=True, padx=15, pady=10)

        tab_nueva = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(tab_nueva, text="  ➕ Nueva Venta  ")
        NuevaVentaPanel(tab_nueva, self.usuario, self._load_historial).pack(fill=BOTH, expand=True)

        tab_hist = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(tab_hist, text="  📋 Historial  ")
        self._build_historial(tab_hist)

    def _build_historial(self, parent):
        toolbar = tk.Frame(parent, bg=CONTENT_BG, pady=10, padx=10)
        toolbar.pack(fill=X)
        tb.Button(toolbar, text="🔄 Actualizar", bootstyle="secondary-outline",
                  command=self._load_historial).pack(side=LEFT)
        tb.Button(toolbar, text="🖨️ Exportar PDF", bootstyle="dark-outline",
                  command=self._exportar_pdf).pack(side=LEFT, padx=5)

        card = tk.Frame(parent, bg='white', highlightbackground='#e0e0e0', highlightthickness=1)
        card.pack(fill=BOTH, expand=True, padx=10, pady=(0,10))

        cols = ['#', 'Fecha', 'Cliente', 'Tipo', 'S/Desc', 'Descuento', 'IVA', 'Total', 'Vendedor']
        keys = ['id', 'fecha', 'cliente', 'tipo_comprobante',
                'subtotal', 'descuento_total', 'iva', 'total', 'usuario']
        self._hist_keys = keys
        frame_tree, self.hist_tree = make_treeview(card, cols, height=20)
        frame_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        widths = {'#': 45, 'Fecha': 125, 'Cliente': 150, 'Tipo': 85,
                  'S/Desc': 85, 'Descuento': 85, 'IVA': 70, 'Total': 85, 'Vendedor': 110}
        for col in cols:
            self.hist_tree.heading(col, text=col)
            self.hist_tree.column(col, width=widths.get(col, 80), anchor='center')
        self.hist_tree.column('Cliente', anchor='w')
        self.hist_tree.column('Vendedor', anchor='w')
        self._ventas_data = []

    def _load_historial(self):
        if not hasattr(self, 'hist_tree'): return
        self._ventas_data = get_ventas()
        rows = []
        for v in self._ventas_data:
            r = dict(v)
            r['subtotal']       = f"Bs.{v['subtotal']:.2f}"
            r['descuento_total']= f"Bs.{v.get('descuento_total',0):.2f}"
            r['iva']            = f"Bs.{v['iva']:.2f}"
            r['total']          = f"Bs.{v['total']:.2f}"
            r['tipo_comprobante'] = '🧾 Factura' if v['tipo_comprobante'] == 'FACTURA' else '📄 Sin Fact.'
            rows.append(r)
        populate_tree(self.hist_tree, rows, self._hist_keys)

    def _exportar_pdf(self):
        sel = self.hist_tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione una venta", parent=self); return
        idx   = self.hist_tree.index(sel[0])
        venta = self._ventas_data[idx]
        detalles = get_detalle_venta(venta['id'])
        path = exportar_venta_pdf(venta, detalles,
                                  venta.get('cliente',''), venta.get('usuario',''),
                                  cliente_direccion=venta.get('cliente_direccion',''),
                                  cliente_telefono=venta.get('cliente_celular',''),
                                  cliente_ci_nit=venta.get('cliente_ci_nit',''))
        messagebox.showinfo("PDF Generado", f"Archivo guardado en:\n{path}", parent=self)
        try:
            if sys.platform == 'win32':   os.startfile(path)
            elif sys.platform == 'darwin': subprocess.run(['open', path])
            else:                          subprocess.run(['xdg-open', path])
        except: pass


# ═══════════════════════════════════════════════════════════════
class NuevaVentaPanel(tk.Frame):
    def __init__(self, parent, usuario, callback_refresh):
        super().__init__(parent, bg=CONTENT_BG)
        self.usuario          = usuario
        self.callback_refresh = callback_refresh
        self.items_venta      = []   # lista de dicts con datos de cada ítem
        self._clientes        = []
        self._productos_filtrados = []
        self._producto_sel    = None
        self._build()

    # ── UI ──────────────────────────────────────────────────────
    def _build(self):
        paned = tk.PanedWindow(self, orient=HORIZONTAL, bg=CONTENT_BG, sashwidth=4)
        paned.pack(fill=BOTH, expand=True, padx=6, pady=6)

        # ── PANEL IZQUIERDO ─────────────────────────────────────
        left = tk.Frame(paned, bg='white', padx=8, pady=8,
                        highlightbackground='#e0e0e0', highlightthickness=1)
        paned.add(left, minsize=330)
        left.columnconfigure(1, weight=1)
        left.columnconfigure(3, weight=1)

        # ── Datos de venta ──────────────────────────────────────
        tk.Label(left, text="DATOS DE LA VENTA", font=("Arial", 9, "bold"),
                 bg='white', fg=HEADER_BG).grid(row=0, column=0, columnspan=4,
                 sticky='w', pady=(0, 8))

        # Cliente
        tk.Label(left, text="Cliente *", font=("Arial", 9, "bold"),
                 bg='white', fg='#555').grid(row=1, column=0, sticky='w', padx=4)
        self._clientes   = get_clientes()
        cliente_names    = [c['nombre'] for c in self._clientes]
        self.cliente_var = tk.StringVar(value=cliente_names[0] if cliente_names else '')
        self.cliente_combo = tb.Combobox(left, textvariable=self.cliente_var,
                                          values=cliente_names, state='readonly',
                                          width=26, font=("Arial", 9))
        self.cliente_combo.grid(row=1, column=1, columnspan=3, sticky='ew', padx=4, pady=3)

        # Comprobante
        tk.Label(left, text="Comprobante *", font=("Arial", 9, "bold"),
                 bg='white', fg='#555').grid(row=2, column=0, sticky='w', padx=4)
        self.tipo_var = tk.StringVar(value='SIN_FACTURA')
        ft = tk.Frame(left, bg='white')
        ft.grid(row=2, column=1, columnspan=3, sticky='w', padx=4, pady=3)
        tb.Radiobutton(ft, text="Sin Factura",  variable=self.tipo_var,
                       value='SIN_FACTURA', bootstyle="dark").pack(side=LEFT)
        tb.Radiobutton(ft, text="Con Factura (+IVA 13%)", variable=self.tipo_var,
                       value='FACTURA', bootstyle="dark").pack(side=LEFT, padx=(10,0))
        self.tipo_var.trace('w', self._on_tipo_change)

        # ── Separador ───────────────────────────────────────────
        tk.Frame(left, bg='#eee', height=1).grid(row=3, column=0, columnspan=4,
                 sticky='ew', pady=8)
        tk.Label(left, text="BUSCAR PRODUCTO", font=("Arial", 9, "bold"),
                 bg='white', fg=HEADER_BG).grid(row=4, column=0, columnspan=4, sticky='w')

        # Búsqueda
        tk.Label(left, text="Buscar", font=("Arial", 9, "bold"),
                 bg='white', fg='#555').grid(row=5, column=0, sticky='w', padx=4, pady=3)
        self.busq_var = tk.StringVar()
        tb.Entry(left, textvariable=self.busq_var, width=30,
                 font=("Arial", 9)).grid(row=5, column=1, columnspan=3,
                 sticky='ew', padx=4)
        self.busq_var.trace('w', self._buscar_producto)

        # ── Lista de productos con info completa ─────────────────
        frame_lista = tk.Frame(left, bg='white',
                               highlightbackground='#ddd', highlightthickness=1)
        frame_lista.grid(row=6, column=0, columnspan=4, sticky='ew', padx=4, pady=4)

        # Scrollbar para la lista
        sb = tk.Scrollbar(frame_lista, orient=VERTICAL)
        sb.pack(side=RIGHT, fill=Y)
        self.prod_listbox = tk.Listbox(
            frame_lista, height=5, font=("Consolas", 8),
            selectbackground='#0f3460', activestyle='none',
            yscrollcommand=sb.set, relief='flat', bd=0)
        self.prod_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        sb.config(command=self.prod_listbox.yview)
        self.prod_listbox.bind('<<ListboxSelect>>', self._on_producto_select)

        # Info del producto seleccionado (recuadro con wrap)
        self.info_frame = tk.Frame(left, bg='#f0f4ff',
                                    highlightbackground='#b0c4de', highlightthickness=1)
        self.info_frame.grid(row=7, column=0, columnspan=4,
                             sticky='ew', padx=4, pady=(1,3))
        self.info_label = tk.Label(
            self.info_frame, text="Seleccione un producto de la lista...",
            font=("Arial", 8), bg='#f0f4ff', fg='#555',
            wraplength=320, justify='left', anchor='w',
            padx=6, pady=5)
        self.info_label.pack(fill=X)

        # Cantidad + Desc individual
        tk.Label(left, text="Cantidad *", font=("Arial", 9, "bold"),
                 bg='white', fg='#555').grid(row=8, column=0, sticky='w', padx=4, pady=3)
        self.cant_var = tk.StringVar(value='1')
        tb.Entry(left, textvariable=self.cant_var, width=9,
                 font=("Arial", 9)).grid(row=8, column=1, sticky='w', padx=4)

        tk.Label(left, text="Desc.individual %", font=("Arial", 9, "bold"),
                 bg='white', fg='#555').grid(row=8, column=2, sticky='w', padx=4)
        self.desc_ind_var = tk.StringVar(value='0')
        self.desc_ind_entry = tb.Entry(left, textvariable=self.desc_ind_var,
                                       width=7, font=("Arial", 9))
        self.desc_ind_entry.grid(row=8, column=3, sticky='w', padx=4)

        tb.Button(left, text="➕ Agregar al carrito", bootstyle="success",
                  command=self._agregar_item).grid(row=9, column=0, columnspan=4,
                  pady=4, ipadx=5)

        # ── PANEL DERECHO ────────────────────────────────────────
        right = tk.Frame(paned, bg='white', padx=8, pady=8,
                         highlightbackground='#e0e0e0', highlightthickness=1)
        paned.add(right, minsize=420)

        # Título + campo descuento global
        top_right = tk.Frame(right, bg='white')
        top_right.pack(fill=X, pady=(0,6))
        tk.Label(top_right, text="🛒 CARRITO", font=("Arial", 9, "bold"),
                 bg='white', fg=HEADER_BG).pack(side=LEFT)

        # Desc global (derecha del título)
        desc_frame = tk.Frame(top_right, bg='white')
        desc_frame.pack(side=RIGHT)
        tk.Label(desc_frame, text="Desc.global %:", font=("Arial", 9, "bold"),
                 bg='white', fg='#555').pack(side=LEFT, padx=(0,4))
        self.desc_global_var = tk.StringVar(value='0')
        self.desc_global_entry = tb.Entry(desc_frame, textvariable=self.desc_global_var,
                                          width=6, font=("Arial", 9))
        self.desc_global_entry.pack(side=LEFT)
        tb.Button(desc_frame, text="Aplicar", bootstyle="warning-outline",
                  command=self._aplicar_desc_global).pack(side=LEFT, padx=(4,0))
        self.desc_global_entry.bind("<Return>", lambda e: self._aplicar_desc_global())


        # Contenedor para CarritoWidget con altura mínima
        cart_container = tk.Frame(right, bg='white')
        cart_container.pack(fill=BOTH, expand=True, pady=(6,0))

        # CarritoWidget — tabla personalizada con descripción completa y multi-línea
        self.cart_widget = CarritoWidget(cart_container,
                                          on_doble_clic=self._editar_item_carrito)
        self.cart_widget.pack(fill=BOTH, expand=True)

        btn_row_cart = tk.Frame(right, bg='white')
        btn_row_cart.pack(anchor='w', pady=(2,0))
        tb.Button(btn_row_cart, text="🗑️ Quitar seleccionado",
                  bootstyle="danger-outline",
                  command=self._quitar_item).pack(side=LEFT, padx=(0,6))
        tb.Button(btn_row_cart, text="✏️ Editar ítem",
                  bootstyle="secondary-outline",
                  command=lambda: self._editar_item_carrito(
                      self.cart_widget.get_selected_index())).pack(side=LEFT)
        tk.Label(btn_row_cart,
                 text="  ← doble clic en ítem para editar",
                 font=("Arial", 7), bg='white', fg='#aaa').pack(side=LEFT, padx=4)

        # Totales
        tk.Frame(right, bg='#eee', height=1).pack(fill=X, pady=2)
        tot_frame = tk.Frame(right, bg='white')
        tot_frame.pack(fill=X, padx=0, pady=0)

        self.lbl_sin_desc  = tk.Label(tot_frame, text="Total s/descuento: Bs. 0.00",
                                       font=("Arial", 8), bg='white', fg='#777')
        self.lbl_sin_desc.pack(anchor='e', pady=1)
        self.lbl_iva       = tk.Label(tot_frame, text="IVA (13%):  Bs. 0.00",
                                       font=("Arial", 8), bg='white', fg='#777')
        self.lbl_iva.pack(anchor='e', pady=1)
        self.lbl_descuento = tk.Label(tot_frame, text="Descuento ahorrado: Bs. 0.00",
                                       font=("Arial", 8, "bold"), bg='white', fg='#e65100')
        self.lbl_descuento.pack(anchor='e', pady=1)
        tk.Frame(right, bg='#ccc', height=1).pack(fill=X)
        self.lbl_total     = tk.Label(tot_frame, text="TOTAL: Bs. 0.00",
                                       font=("Arial", 11, "bold"), bg='white', fg=HEADER_BG)
        self.lbl_total.pack(anchor='e', pady=(2,0))

        # Botones finales
        btn_row = tk.Frame(right, bg='white')
        btn_row.pack(fill=X, pady=(3,0))
        tb.Button(btn_row, text="✅ REGISTRAR VENTA", bootstyle="dark",
                  command=self._registrar).pack(side=LEFT, ipadx=6, ipady=5)
        tb.Button(btn_row, text="🗑️ Limpiar Todo", bootstyle="danger-outline",
                  command=self._limpiar).pack(side=LEFT, padx=8)

        # Carga inicial
        self._buscar_producto()

    # ── Eventos ─────────────────────────────────────────────────
    def _on_tipo_change(self, *args):
        es_factura = self.tipo_var.get() == 'FACTURA'
        # Bloquear desc individual y global si es factura
        state = 'disabled' if es_factura else 'normal'
        self.desc_ind_entry.config(state=state)
        self.desc_global_entry.config(state=state)
        if es_factura:
            self.desc_ind_var.set('0')
            self.desc_global_var.set('0')
            # Poner todos los descuentos en 0 sin borrar el carrito
            for item in self.items_venta:
                item['pct_descuento'] = 0
                item['precio_final']  = item['precio_venta_original']
                item['descuento_bs']  = 0
        self._refresh_carrito()

    def _buscar_producto(self, *args):
        self._productos_filtrados = get_productos(
            solo_activos=True, busqueda=self.busq_var.get())
        self.prod_listbox.delete(0, END)
        for p in self._productos_filtrados:
            cod  = p.get('codigo_proveedor') or p.get('codigo_tienda') or ''
            desc = p['descripcion']
            # Truncar descripción para que quepa en una línea del listbox
            desc_corta = desc if len(desc) <= 35 else desc[:33] + '…'
            marca = p.get('marca') or ''
            self.prod_listbox.insert(
                END,
                f"{cod:<14} {desc_corta:<36} St:{p['stock']:<4} Bs.{p['precio_venta']:.2f}")

    def _on_producto_select(self, event):
        sel = self.prod_listbox.curselection()
        if not sel: return
        p = self._productos_filtrados[sel[0]]
        self._producto_sel = p
        cod   = p.get('codigo_proveedor') or p.get('codigo_tienda') or '—'
        marca = p.get('marca') or '—'
        info  = (f"Cód: {cod}   Marca: {marca}   Stock: {p['stock']}   "
                 f"Precio: Bs.{p['precio_venta']:.2f}\n"
                 f"Desc.máx negociable: {p.get('descuento_maximo',0):.0f}%  |  "
                 f"Descripción: {p['descripcion']}")
        self.info_label.config(text=info, fg='#1a1a2e')

        # Autocompletar descuento del cliente (en % sobre margen negociable)
        if self.tipo_var.get() == 'SIN_FACTURA':
            cliente_nombre = self.cliente_var.get()
            cliente = next((c for c in self._clientes if c['nombre'] == cliente_nombre), None)
            if cliente:
                desc_cat = cliente.get('descuento_cat') or 0
                # desc_cat es % sobre margen negociable, limitado al máximo del producto
                max_pct = 100.0  # el 100% del margen negociable es el tope
                aplicar = min(desc_cat, max_pct)
                self.desc_ind_var.set(str(int(aplicar)))

    def _agregar_item(self):
        if not self._producto_sel:
            messagebox.showwarning("Atención", "Seleccione un producto", parent=self); return
        try:
            cant = int(self.cant_var.get())
            pct  = float(self.desc_ind_var.get())
        except:
            messagebox.showwarning("Error", "Cantidad y descuento deben ser numéricos", parent=self); return

        p = self._producto_sel
        if cant <= 0:
            messagebox.showwarning("Error", "La cantidad debe ser mayor a 0", parent=self); return
        if cant > p['stock']:
            messagebox.showwarning("Error", f"Stock insuficiente. Disponible: {p['stock']}", parent=self); return
        if pct < 0 or pct > 100:
            messagebox.showwarning("Error", "El descuento debe estar entre 0 y 100%", parent=self); return

        # ── Producto sin precio: exigir precio manual ──────────────
        if p['precio_venta'] == 0:
            precio_manual = _pedir_precio(self, p['descripcion'])
            if precio_manual is None: return   # canceló
            # Aplicar precio manual como precio_venta temporal
            p = dict(p)
            p['precio_venta']  = precio_manual
            p['precio_compra'] = precio_manual  # base para cálculo
            # Sin descuento si no hay precio establecido
            pct = 0

        if self.tipo_var.get() == 'FACTURA':
            pct = 0

        precio_final, desc_bs, precio_original = calcular_precio_con_descuento(p, pct)

        # Si ya está en carrito → sumar cantidad
        for item in self.items_venta:
            if item['producto_id'] == p['id']:
                nueva_cant = item['cantidad'] + cant
                if nueva_cant > p['stock']:
                    messagebox.showwarning("Error", "Stock insuficiente", parent=self); return
                item['cantidad'] = nueva_cant
                self._refresh_carrito()
                return

        self.items_venta.append({
            'producto_id':           p['id'],
            'descripcion':           p['descripcion'],
            'descripcion_venta':     p['descripcion'],   # editable por ítem
            'marca_venta':           p.get('marca') or '',
            'codigo_proveedor':      p.get('codigo_proveedor') or p.get('codigo_tienda') or '',
            'unidad_medida':         p.get('unidad_medida') or '',
            'precio_venta_original': precio_original,
            'precio_compra':         p['precio_compra'],
            'porcentaje_venta':      p['porcentaje_venta'],
            'descuento_maximo':      p['descuento_maximo'],
            'precio_venta':          p['precio_venta'],
            'precio_final':          precio_final,
            'descuento_bs':          desc_bs,
            'pct_descuento':         pct,
            'cantidad':              cant,
        })
        self._refresh_carrito()
        self.cant_var.set('1')
        self.desc_ind_var.set('0')

    def _aplicar_desc_global(self):
        """Aplica el % del campo global a TODOS los ítems del carrito."""
        if not self.items_venta:
            return
        if self.tipo_var.get() == 'FACTURA':
            return
        try:
            pct = float(self.desc_global_var.get())
        except:
            messagebox.showwarning("Error", "Valor de descuento inválido", parent=self); return
        if pct < 0 or pct > 100:
            messagebox.showwarning("Error", "El descuento debe estar entre 0 y 100%", parent=self); return

        for item in self.items_venta:
            pf, db, po = calcular_precio_con_descuento(item, pct)
            item['pct_descuento'] = pct
            item['precio_final']  = pf
            item['descuento_bs']  = db
        self._refresh_carrito()

    def _quitar_item(self):
        idx = self.cart_widget.get_selected_index()
        if idx is not None and 0 <= idx < len(self.items_venta):
            self.items_venta.pop(idx)
            self._refresh_carrito()
        else:
            import tkinter.messagebox as mb
            mb.showwarning("Atención", "Seleccione un ítem del carrito", parent=self)

    def _refresh_carrito(self):
        self.cart_widget.set_items(self.items_venta)
        self._update_totales()

    def _editar_item_carrito(self, idx):
        if idx is None or idx < 0 or idx >= len(self.items_venta):
            messagebox.showwarning("Atención", "Seleccione un ítem del carrito", parent=self)
            return
        item = self.items_venta[idx]
        _editar_item_dialog(self, item, self._refresh_carrito)

    def _update_totales(self):
        total_sin_desc = sum(i['cantidad'] * i['precio_venta_original'] for i in self.items_venta)
        total_con_desc = sum(i['cantidad'] * i['precio_final']          for i in self.items_venta)
        ahorro         = total_sin_desc - total_con_desc

        es_factura = self.tipo_var.get() == 'FACTURA'
        iva        = total_con_desc * 0.13 if es_factura else 0
        total_pagar= total_con_desc + iva

        self.lbl_sin_desc.config( text=f"Total s/descuento:    Bs. {total_sin_desc:.2f}")
        self.lbl_iva.config(      text=f"IVA (13%):            Bs. {iva:.2f}")
        self.lbl_descuento.config(text=f"Descuento ahorrado:   Bs. {ahorro:.2f}")
        self.lbl_total.config(    text=f"TOTAL:  Bs. {total_pagar:.2f}")

    def _limpiar(self):
        self.items_venta.clear()
        self._refresh_carrito()
        self.busq_var.set('')
        self.desc_global_var.set('0')

    def _registrar(self):
        if not self.items_venta:
            messagebox.showwarning("Atención", "El carrito está vacío", parent=self); return
        cliente_nombre = self.cliente_var.get()
        cliente = next((c for c in self._clientes if c['nombre'] == cliente_nombre), None)
        if not cliente:
            messagebox.showwarning("Error", "Seleccione un cliente", parent=self); return

        tipo = self.tipo_var.get()

        # Calcular totales para confirmación
        total_sin = sum(i['cantidad'] * i['precio_venta_original'] for i in self.items_venta)
        total_con = sum(i['cantidad'] * i['precio_final']          for i in self.items_venta)
        ahorro    = total_sin - total_con
        iva       = total_con * 0.13 if tipo == 'FACTURA' else 0
        total_pay = total_con + iva

        confirm = messagebox.askyesno(
            "Confirmar Venta",
            f"Cliente: {cliente_nombre}\n"
            f"Tipo:    {tipo}\n"
            f"Ítems:   {len(self.items_venta)}\n"
            f"─────────────────────\n"
            f"S/Desc:  Bs. {total_sin:.2f}\n"
            f"Ahorro:  Bs. {ahorro:.2f}\n"
            f"IVA:     Bs. {iva:.2f}\n"
            f"TOTAL:   Bs. {total_pay:.2f}",
            parent=self)
        if not confirm: return

        detalles = [{
            'producto_id':             i['producto_id'],
            'cantidad':                i['cantidad'],
            'precio_venta':            i['precio_venta_original'],
            'descuento_aplicado':      i['pct_descuento'],
            'precio_final':            i['precio_final'],
            'descripcion_override':    i.get('descripcion_venta') or None,
            'unidad_medida_override':  i.get('unidad_medida') or None,
            'marca_override':          i.get('marca_venta') or None,
        } for i in self.items_venta]

        venta_id = registrar_venta(cliente['id'], self.usuario['id'], tipo, detalles)
        messagebox.showinfo("✅ Venta Registrada",
                            f"Venta #{venta_id} registrada correctamente", parent=self)

        if messagebox.askyesno("PDF", "¿Desea exportar el comprobante en PDF?", parent=self):
            ventas = get_ventas()
            venta_data = next((v for v in ventas if v['id'] == venta_id), {})
            detalles_v = get_detalle_venta(venta_id)
            path = exportar_venta_pdf(
                venta_data, detalles_v,
                cliente_nombre, self.usuario['nombre'],
                cliente_direccion=cliente.get('direccion',''),
                cliente_telefono=cliente.get('celular',''),
                cliente_ci_nit=cliente.get('ci_nit',''))
            messagebox.showinfo("PDF", f"Guardado en:\n{path}", parent=self)
            try:
                if sys.platform == 'win32': os.startfile(path)
            except: pass

        self._limpiar()
        self._buscar_producto()
        self.callback_refresh()
