import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
from views.base_view import *
from views.ventas_view import calcular_precio_con_descuento, _pedir_precio, _pedir_descripcion, _editar_item_dialog
from views.carrito_widget import CarritoWidget
from controllers.controller import *
from utils.pdf_export import exportar_cotizacion_pdf
import os, subprocess, sys

class CotizacionesView(tk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent, bg=CONTENT_BG)
        self.usuario   = usuario
        self._cots_data = []
        self._build()
        self._load_historial()

    def _build(self):
        make_page_header(self, "📋 Cotizaciones", "Generar y gestionar cotizaciones").pack(fill=X)
        notebook = tb.Notebook(self, bootstyle="dark")
        notebook.pack(fill=BOTH, expand=True, padx=15, pady=10)

        tab_nueva = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(tab_nueva, text="  ➕ Nueva Cotización  ")
        NuevaCotizacionPanel(tab_nueva, self.usuario, self._load_historial).pack(fill=BOTH, expand=True)

        tab_list = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(tab_list, text="  📋 Listado  ")
        self._build_listado(tab_list)

    def _build_listado(self, parent):
        toolbar = tk.Frame(parent, bg=CONTENT_BG, pady=10, padx=10)
        toolbar.pack(fill=X)
        tb.Button(toolbar, text="🔄 Actualizar",      bootstyle="secondary-outline",
                  command=self._load_historial).pack(side=LEFT)
        tb.Button(toolbar, text="🖨️ Exportar PDF",    bootstyle="dark-outline",
                  command=self._export_pdf).pack(side=LEFT, padx=5)
        tb.Button(toolbar, text="✅ Convertir a Venta", bootstyle="success-outline",
                  command=self._convertir).pack(side=LEFT, padx=5)

        card = tk.Frame(parent, bg='white',
                        highlightbackground='#e0e0e0', highlightthickness=1)
        card.pack(fill=BOTH, expand=True, padx=10, pady=(0,10))

        cols = ['#', 'Fecha', 'Cliente', 'Estado', 'S/Desc', 'Descuento', 'Total']
        self._hist_keys = ['id', 'fecha', 'cliente', 'estado',
                           'subtotal', 'descuento_total', 'total']
        frame_tree, self.hist_tree = make_treeview(card, cols, height=18)
        frame_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        widths = {'#': 45, 'Fecha': 130, 'Cliente': 180, 'Estado': 90,
                  'S/Desc': 90, 'Descuento': 85, 'Total': 90}
        for col in cols:
            self.hist_tree.heading(col, text=col)
            self.hist_tree.column(col, width=widths.get(col,90), anchor='center')
        self.hist_tree.column('Cliente', anchor='w')

    def _load_historial(self):
        if not hasattr(self, 'hist_tree'): return
        self._cots_data = get_cotizaciones()
        rows = []
        for c in self._cots_data:
            r = dict(c)
            r['subtotal']        = f"Bs.{c.get('subtotal', c['total']):.2f}"
            r['descuento_total'] = f"Bs.{c.get('descuento_total', 0):.2f}"
            r['total']           = f"Bs.{c['total']:.2f}"
            r['estado'] = '✅ Activa' if c['estado'] == 'ACTIVA' else '🔄 Convertida'
            rows.append(r)
        populate_tree(self.hist_tree, rows, self._hist_keys)

    def _get_sel_cot(self):
        sel = self.hist_tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione una cotización", parent=self)
            return None
        return self._cots_data[self.hist_tree.index(sel[0])]

    def _export_pdf(self):
        cot = self._get_sel_cot()
        if not cot: return
        detalles = get_detalle_cotizacion(cot['id'])
        path = exportar_cotizacion_pdf(
            cot, detalles, cot.get('cliente',''),
            cliente_direccion=cot.get('cliente_direccion',''),
            cliente_telefono=cot.get('cliente_celular',''),
            cliente_ci_nit=cot.get('cliente_ci_nit',''))
        messagebox.showinfo("PDF", f"Guardado en:\n{path}", parent=self)
        try:
            if sys.platform == 'win32':    os.startfile(path)
            elif sys.platform == 'darwin': subprocess.run(['open', path])
            else:                          subprocess.run(['xdg-open', path])
        except: pass

    def _convertir(self):
        cot = self._get_sel_cot()
        if not cot: return
        if cot['estado'] != 'ACTIVA':
            messagebox.showwarning("Atención", "Solo se pueden convertir cotizaciones activas",
                                   parent=self); return
        tipo = 'SIN_FACTURA'
        if messagebox.askyesno("Tipo de comprobante",
                               "¿La venta es CON FACTURA?\n(Sí = Factura  |  No = Sin factura)",
                               parent=self):
            tipo = 'FACTURA'
        venta_id = convertir_cotizacion_a_venta(cot['id'], self.usuario['id'], tipo)
        messagebox.showinfo("✅ Éxito",
                            f"Cotización #{cot['id']} convertida en Venta #{venta_id}",
                            parent=self)
        self._load_historial()


# ═══════════════════════════════════════════════════════════════
class NuevaCotizacionPanel(tk.Frame):
    """Panel idéntico al de ventas pero SIN bajar stock."""

    def __init__(self, parent, usuario, callback_refresh):
        super().__init__(parent, bg=CONTENT_BG)
        self.usuario          = usuario
        self.callback_refresh = callback_refresh
        self.items            = []
        self._clientes        = []
        self._productos_filtrados = []
        self._producto_sel    = None
        self._build()

    # ── UI ──────────────────────────────────────────────────────
    def _build(self):
        paned = tk.PanedWindow(self, orient=HORIZONTAL, bg=CONTENT_BG, sashwidth=5)
        paned.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # ── PANEL IZQUIERDO ─────────────────────────────────────
        left = tk.Frame(paned, bg='white', padx=8, pady=8,
                        highlightbackground='#e0e0e0', highlightthickness=1)
        paned.add(left, minsize=330)
        left.columnconfigure(1, weight=1)
        left.columnconfigure(3, weight=1)

        tk.Label(left, text="DATOS DE LA COTIZACIÓN", font=("Arial", 9, "bold"),
                 bg='white', fg=HEADER_BG).grid(row=0, column=0, columnspan=4,
                 sticky='w', pady=(0, 8))

        # Cliente
        tk.Label(left, text="Cliente *", font=("Arial", 9, "bold"),
                 bg='white', fg='#555').grid(row=1, column=0, sticky='w', padx=4)
        self._clientes   = get_clientes()
        cliente_names    = [c['nombre'] for c in self._clientes]
        self.cliente_var = tk.StringVar(value=cliente_names[0] if cliente_names else '')
        tb.Combobox(left, textvariable=self.cliente_var, values=cliente_names,
                    state='readonly', width=26,
                    font=("Arial", 9)).grid(row=1, column=1, columnspan=3,
                    sticky='ew', padx=4, pady=3)

        # Separador
        tk.Frame(left, bg='#eee', height=1).grid(row=2, column=0, columnspan=4,
                 sticky='ew', pady=8)
        tk.Label(left, text="BUSCAR PRODUCTO", font=("Arial", 9, "bold"),
                 bg='white', fg=HEADER_BG).grid(row=3, column=0, columnspan=4, sticky='w')

        # Búsqueda
        tk.Label(left, text="Buscar", font=("Arial", 9, "bold"),
                 bg='white', fg='#555').grid(row=4, column=0, sticky='w', padx=4, pady=3)
        self.busq_var = tk.StringVar()
        tb.Entry(left, textvariable=self.busq_var, width=30,
                 font=("Arial", 9)).grid(row=4, column=1, columnspan=3,
                 sticky='ew', padx=4)
        self.busq_var.trace('w', self._buscar)

        # Lista productos con scrollbar
        frame_lista = tk.Frame(left, bg='white',
                               highlightbackground='#ddd', highlightthickness=1)
        frame_lista.grid(row=5, column=0, columnspan=4, sticky='ew', padx=4, pady=4)
        sb = tk.Scrollbar(frame_lista, orient=VERTICAL)
        sb.pack(side=RIGHT, fill=Y)
        self.prod_listbox = tk.Listbox(
            frame_lista, height=5, font=("Consolas", 8),
            selectbackground='#0f3460', activestyle='none',
            yscrollcommand=sb.set, relief='flat', bd=0)
        self.prod_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        sb.config(command=self.prod_listbox.yview)
        self.prod_listbox.bind('<<ListboxSelect>>', self._on_select)

        # Info producto seleccionado
        self.info_frame = tk.Frame(left, bg='#f0f4ff',
                                    highlightbackground='#b0c4de', highlightthickness=1)
        self.info_frame.grid(row=6, column=0, columnspan=4,
                             sticky='ew', padx=4, pady=(1, 3))
        self.info_label = tk.Label(
            self.info_frame,
            text="Seleccione un producto de la lista...",
            font=("Arial", 8), bg='#f0f4ff', fg='#555',
            wraplength=320, justify='left', anchor='w', padx=6, pady=5)
        self.info_label.pack(fill=X)

        # Cantidad + descuento individual
        tk.Label(left, text="Cantidad *", font=("Arial", 9, "bold"),
                 bg='white', fg='#555').grid(row=7, column=0, sticky='w', padx=4, pady=3)
        self.cant_var = tk.StringVar(value='1')
        tb.Entry(left, textvariable=self.cant_var, width=9,
                 font=("Arial", 9)).grid(row=7, column=1, sticky='w', padx=4)

        tk.Label(left, text="Desc.individual %", font=("Arial", 9, "bold"),
                 bg='white', fg='#555').grid(row=7, column=2, sticky='w', padx=4)
        self.desc_ind_var = tk.StringVar(value='0')
        tb.Entry(left, textvariable=self.desc_ind_var, width=7,
                 font=("Arial", 9)).grid(row=7, column=3, sticky='w', padx=4)

        tb.Button(left, text="➕ Agregar a la cotización", bootstyle="success",
                  command=self._agregar).grid(row=8, column=0, columnspan=4, pady=4, ipadx=5)

        # ── PANEL DERECHO ────────────────────────────────────────
        right = tk.Frame(paned, bg='white', padx=8, pady=8,
                         highlightbackground='#e0e0e0', highlightthickness=1)
        paned.add(right, minsize=420)

        # Título + descuento global
        top_right = tk.Frame(right, bg='white')
        top_right.pack(fill=X, pady=(0, 6))
        tk.Label(top_right, text="📋 COTIZACIÓN", font=("Arial", 9, "bold"),
                 bg='white', fg=HEADER_BG).pack(side=LEFT)

        desc_frame = tk.Frame(top_right, bg='white')
        desc_frame.pack(side=RIGHT)
        tk.Label(desc_frame, text="Desc.global %:", font=("Arial", 9, "bold"),
                 bg='white', fg='#555').pack(side=LEFT, padx=(0, 4))
        self.desc_global_var = tk.StringVar(value='0')
        self.desc_global_entry = tb.Entry(
            desc_frame, textvariable=self.desc_global_var, width=6, font=("Arial", 9))
        self.desc_global_entry.pack(side=LEFT)
        tb.Button(desc_frame, text="Aplicar", bootstyle="warning-outline",
                  command=self._aplicar_desc_global).pack(side=LEFT, padx=(4, 0))
        self.desc_global_entry.bind("<Return>", lambda e: self._aplicar_desc_global())

        # Treeview — mismas columnas que ventas
        self.cart_widget = CarritoWidget(right,
                                          on_doble_clic=self._editar_item_carrito)
        self.cart_widget.pack(fill=BOTH, expand=True)

        btn_row_cot = tk.Frame(right, bg='white')
        btn_row_cot.pack(anchor='w', pady=(5, 0))
        tb.Button(btn_row_cot, text="🗑️ Quitar seleccionado",
                  bootstyle="danger-outline",
                  command=self._quitar).pack(side=LEFT, padx=(0,6))
        tb.Button(btn_row_cot, text="✏️ Editar ítem",
                  bootstyle="secondary-outline",
                  command=lambda: self._editar_item_carrito(
                      self.cart_widget.get_selected_index())).pack(side=LEFT)
        tk.Label(btn_row_cot,
                 text="  ← doble clic en ítem para editar",
                 font=("Arial", 7), bg='white', fg='#aaa').pack(side=LEFT, padx=4)

        # Totales — idénticos a ventas
        tk.Frame(right, bg='#eee', height=1).pack(fill=X, pady=4)
        tot_frame = tk.Frame(right, bg='white')
        tot_frame.pack(fill=X)

        self.lbl_sin_desc  = tk.Label(tot_frame, text="Total s/descuento: Bs. 0.00",
                                       font=("Arial", 9), bg='white', fg='#777')
        self.lbl_sin_desc.pack(anchor='e')
        self.lbl_descuento = tk.Label(tot_frame, text="Descuento ahorrado: Bs. 0.00",
                                       font=("Arial", 9, "bold"), bg='white', fg='#e65100')
        self.lbl_descuento.pack(anchor='e')
        tk.Frame(right, bg='#ccc', height=1).pack(fill=X)
        self.lbl_total = tk.Label(tot_frame, text="TOTAL: Bs. 0.00",
                                   font=("Arial", 11, "bold"), bg='white', fg=HEADER_BG)
        self.lbl_total.pack(anchor='e', pady=(4, 0))

        btn_row = tk.Frame(right, bg='white')
        btn_row.pack(fill=X, pady=(6, 0))
        tb.Button(btn_row, text="💾 GUARDAR COTIZACIÓN", bootstyle="dark",
                  command=self._guardar).pack(side=LEFT, ipadx=6, ipady=5)
        tb.Button(btn_row, text="🗑️ Limpiar Todo", bootstyle="danger-outline",
                  command=self._limpiar).pack(side=LEFT, padx=8)

        self._buscar()

    # ── Eventos ─────────────────────────────────────────────────
    def _buscar(self, *args):
        self._productos_filtrados = get_productos(
            solo_activos=True, busqueda=self.busq_var.get())
        self.prod_listbox.delete(0, END)
        for p in self._productos_filtrados:
            cod        = p.get('codigo_proveedor') or p.get('codigo_tienda') or ''
            desc_corta = p['descripcion'] if len(p['descripcion']) <= 35 \
                         else p['descripcion'][:33] + '…'
            self.prod_listbox.insert(
                END,
                f"{cod:<14} {desc_corta:<36} St:{p['stock']:<4} Bs.{p['precio_venta']:.2f}")

    def _on_select(self, event):
        sel = self.prod_listbox.curselection()
        if not sel: return
        p = self._productos_filtrados[sel[0]]
        self._producto_sel = p
        cod   = p.get('codigo_proveedor') or p.get('codigo_tienda') or '—'
        marca = p.get('marca') or '—'
        info  = (f"Cód: {cod}   Marca: {marca}   Stock: {p['stock']}   "
                 f"Precio: Bs.{p['precio_venta']:.2f}\n"
                 f"Desc.máx negociable: {p.get('descuento_maximo', 0):.0f}%  |  "
                 f"Descripción: {p['descripcion']}")
        self.info_label.config(text=info, fg='#1a1a2e')

        # Autocompletar descuento del cliente
        cliente_nombre = self.cliente_var.get()
        cliente = next((c for c in self._clientes if c['nombre'] == cliente_nombre), None)
        if cliente:
            desc_cat = cliente.get('descuento_cat') or 0
            self.desc_ind_var.set(str(int(min(desc_cat, 100))))

    def _agregar(self):
        if not self._producto_sel:
            messagebox.showwarning("Atención", "Seleccione un producto", parent=self); return
        try:
            cant = int(self.cant_var.get())
            pct  = float(self.desc_ind_var.get())
        except:
            messagebox.showwarning("Error", "Valores numéricos inválidos", parent=self); return

        p = self._producto_sel
        if cant <= 0:
            messagebox.showwarning("Error", "La cantidad debe ser mayor a 0", parent=self); return
        if pct < 0 or pct > 100:
            messagebox.showwarning("Error", "El descuento debe estar entre 0 y 100%", parent=self); return

        # Producto sin precio: exigir precio manual
        if p['precio_venta'] == 0:
            precio_manual = _pedir_precio(self, p['descripcion'])
            if precio_manual is None: return
            p = dict(p)
            p['precio_venta'] = precio_manual
            p['precio_compra'] = precio_manual
            pct = 0

        precio_final, desc_bs, precio_original = calcular_precio_con_descuento(p, pct)

        # Si ya está → sumar cantidad
        for item in self.items:
            if item['producto_id'] == p['id']:
                item['cantidad'] += cant
                self._refresh()
                return

        self.items.append({
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
            'precio':                precio_final,
        })
        self._refresh()
        self.cant_var.set('1')
        self.desc_ind_var.set('0')

    def _aplicar_desc_global(self):
        if not self.items: return
        try:
            pct = float(self.desc_global_var.get())
        except:
            messagebox.showwarning("Error", "Valor inválido", parent=self); return
        if pct < 0 or pct > 100:
            messagebox.showwarning("Error", "El descuento debe estar entre 0 y 100%", parent=self); return
        for item in self.items:
            pf, db, po = calcular_precio_con_descuento(item, pct)
            item['pct_descuento'] = pct
            item['precio_final']  = pf
            item['descuento_bs']  = db
            item['precio']        = pf
        self._refresh()

    def _quitar(self):
        idx = self.cart_widget.get_selected_index()
        if idx is not None and 0 <= idx < len(self.items):
            self.items.pop(idx)
            self._refresh()
        else:
            messagebox.showwarning("Atención", "Seleccione un ítem del carrito", parent=self)

    def _refresh(self):
        self.cart_widget.set_items(self.items)
        self._update_totales()

    def _editar_item_carrito(self, idx):
        if idx is None or idx < 0 or idx >= len(self.items):
            messagebox.showwarning("Atención", "Seleccione un ítem del carrito", parent=self)
            return
        item = self.items[idx]
        _editar_item_dialog(self, item, self._refresh)

    def _update_totales(self):
        total_sin = sum(i['cantidad'] * i['precio_venta_original'] for i in self.items)
        total_con = sum(i['cantidad'] * i['precio_final']          for i in self.items)
        ahorro    = total_sin - total_con
        self.lbl_sin_desc.config( text=f"Total s/descuento:    Bs. {total_sin:.2f}")
        self.lbl_descuento.config(text=f"Descuento ahorrado:   Bs. {ahorro:.2f}")
        self.lbl_total.config(    text=f"TOTAL:  Bs. {total_con:.2f}")

    def _limpiar(self):
        self.items.clear()
        self._refresh()
        self.busq_var.set('')
        self.desc_global_var.set('0')

    def _guardar(self):
        if not self.items:
            messagebox.showwarning("Atención", "Agregue productos", parent=self); return
        cliente_nombre = self.cliente_var.get()
        cliente = next((c for c in self._clientes if c['nombre'] == cliente_nombre), None)
        if not cliente:
            messagebox.showwarning("Error", "Seleccione un cliente", parent=self); return

        total_sin = sum(i['cantidad'] * i['precio_venta_original'] for i in self.items)
        total_con = sum(i['cantidad'] * i['precio_final']          for i in self.items)
        ahorro    = total_sin - total_con

        confirm = messagebox.askyesno(
            "Confirmar Cotización",
            f"Cliente: {cliente_nombre}\n"
            f"Ítems:   {len(self.items)}\n"
            f"──────────────────────\n"
            f"S/Desc:  Bs. {total_sin:.2f}\n"
            f"Ahorro:  Bs. {ahorro:.2f}\n"
            f"TOTAL:   Bs. {total_con:.2f}",
            parent=self)
        if not confirm: return

        detalles_cot = [{
            'producto_id':            i['producto_id'],
            'descripcion':            i.get('descripcion_venta') or i['descripcion'],
            'cantidad':               i['cantidad'],
            'precio':                 i['precio'],
            'precio_venta_original':  i['precio_venta_original'],
            'descripcion_override':   i.get('descripcion_venta') or None,
            'unidad_medida_override': i.get('unidad_medida') or None,
            'marca_override':         i.get('marca_venta') or None,
        } for i in self.items]
        cot_id = registrar_cotizacion(cliente['id'], detalles_cot)
        messagebox.showinfo("✅ Guardada", f"Cotización #{cot_id} guardada correctamente",
                            parent=self)
        self._limpiar()
        self._buscar()
        self.callback_refresh()
