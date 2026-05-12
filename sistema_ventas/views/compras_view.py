import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
from views.base_view import *
from controllers.controller import *

class ComprasView(tk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent, bg=CONTENT_BG)
        self.usuario  = usuario
        self.es_admin = usuario['rol'] == 'ADMIN'
        self.items_compra = []
        self._proveedores = []
        self._productos_filtrados = []
        self._producto_sel = None
        self._build()
        self._load_historial()

    def _build(self):
        if self.es_admin:
            make_page_header(self, "📦 Compras",
                             "Registrar compras y actualizar inventario").pack(fill=X)
        else:
            make_page_header(self, "📦 Entrada de Stock",
                             "Aumentar stock de productos").pack(fill=X)

        notebook = tb.Notebook(self, bootstyle="dark")
        notebook.pack(fill=BOTH, expand=True, padx=15, pady=10)

        tab_nueva = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(tab_nueva,
                     text="  ➕ Nueva Compra  " if self.es_admin
                     else "  ➕ Entrada de Stock  ")
        self._build_nueva(tab_nueva)

        tab_hist = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(tab_hist, text="  📋 Historial  ")
        self._build_historial_tab(tab_hist)

    # ── Panel nueva compra ───────────────────────────────────────
    def _build_nueva(self, parent):
        paned = tk.PanedWindow(parent, orient=HORIZONTAL,
                               bg=CONTENT_BG, sashwidth=4)
        paned.pack(fill=BOTH, expand=True, padx=6, pady=6)

        # ── Izquierda ──
        left = tk.Frame(paned, bg='white', padx=10, pady=10,
                        highlightbackground='#e0e0e0', highlightthickness=1)
        paned.add(left, minsize=320)
        left.columnconfigure(1, weight=1)
        left.columnconfigure(3, weight=1)

        row = 0
        tk.Label(left,
                 text="DATOS DE LA COMPRA" if self.es_admin else "ENTRADA DE STOCK",
                 font=("Arial", 9, "bold"),
                 bg='white', fg=HEADER_BG).grid(
                 row=row, column=0, columnspan=4, sticky='w', pady=(0,8))
        row += 1

        # Proveedor — solo ADMIN
        if self.es_admin:
            tk.Label(left, text="Proveedor *", font=("Arial", 9, "bold"),
                     bg='white', fg='#555').grid(row=row, column=0, sticky='w', padx=4)
            self._proveedores = get_proveedores()
            prov_names = [p['nombre'] for p in self._proveedores]
            self.prov_var = tk.StringVar(
                value=prov_names[0] if prov_names else '')
            tb.Combobox(left, textvariable=self.prov_var, values=prov_names,
                        state='readonly', width=26,
                        font=("Arial", 9)).grid(row=row, column=1, columnspan=3,
                        sticky='ew', padx=4, pady=3)
            row += 1

        tk.Frame(left, bg='#eee', height=1).grid(
            row=row, column=0, columnspan=4, sticky='ew', pady=6)
        row += 1

        tk.Label(left, text="BUSCAR PRODUCTO", font=("Arial", 9, "bold"),
                 bg='white', fg=HEADER_BG).grid(
                 row=row, column=0, columnspan=4, sticky='w')
        row += 1

        tk.Label(left, text="Buscar", font=("Arial", 9, "bold"),
                 bg='white', fg='#555').grid(row=row, column=0, sticky='w', padx=4, pady=3)
        self.busq_var = tk.StringVar()
        tb.Entry(left, textvariable=self.busq_var, width=28,
                 font=("Arial", 9)).grid(row=row, column=1, columnspan=3,
                 sticky='ew', padx=4)
        self.busq_var.trace('w', self._buscar_producto)
        row += 1

        frame_lista = tk.Frame(left, bg='white',
                               highlightbackground='#ddd', highlightthickness=1)
        frame_lista.grid(row=row, column=0, columnspan=4,
                         sticky='ew', padx=4, pady=4)
        sb = tk.Scrollbar(frame_lista, orient=VERTICAL)
        sb.pack(side=RIGHT, fill=Y)
        self.prod_listbox = tk.Listbox(
            frame_lista, height=5, font=("Consolas", 8),
            selectbackground='#0f3460', activestyle='none',
            yscrollcommand=sb.set, relief='flat', bd=0)
        self.prod_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        sb.config(command=self.prod_listbox.yview)
        self.prod_listbox.bind('<<ListboxSelect>>', self._on_producto_select)
        row += 1

        # Info producto
        self.info_label = tk.Label(
            left, text="Seleccione un producto...",
            font=("Arial", 8), bg='#f0f4ff', fg='#555',
            wraplength=280, justify='left', anchor='w', padx=6, pady=4,
            highlightbackground='#b0c4de', highlightthickness=1)
        self.info_label.grid(row=row, column=0, columnspan=4,
                             sticky='ew', padx=4, pady=(2,6))
        row += 1

        # Cantidad
        tk.Label(left, text="Cantidad *", font=("Arial", 9, "bold"),
                 bg='white', fg='#555').grid(row=row, column=0, sticky='w', padx=4, pady=3)
        self.cant_var = tk.StringVar(value='1')
        tb.Entry(left, textvariable=self.cant_var, width=10,
                 font=("Arial", 9)).grid(row=row, column=1, sticky='w', padx=4)

        # Costo unitario — solo ADMIN
        if self.es_admin:
            tk.Label(left, text="Costo Unit. *", font=("Arial", 9, "bold"),
                     bg='white', fg='#555').grid(row=row, column=2, sticky='w', padx=4)
            self.costo_var = tk.StringVar(value='0')
            tb.Entry(left, textvariable=self.costo_var, width=10,
                     font=("Arial", 9)).grid(row=row, column=3, sticky='w', padx=4)
        row += 1

        tb.Button(left, text="➕ Agregar", bootstyle="success",
                  command=self._agregar_item).grid(
                  row=row, column=0, columnspan=4, pady=6)

        # ── Derecha ──
        right = tk.Frame(paned, bg='white', padx=10, pady=10,
                         highlightbackground='#e0e0e0', highlightthickness=1)
        paned.add(right, minsize=340)

        tk.Label(right,
                 text="📋 DETALLE" if self.es_admin else "📋 PRODUCTOS A INGRESAR",
                 font=("Arial", 9, "bold"),
                 bg='white', fg=HEADER_BG).pack(anchor='w', pady=(0,6))

        if self.es_admin:
            cols = ['Descripción', 'Cant.', 'Costo Unit.', 'Total']
        else:
            cols = ['Descripción', 'Cantidad a ingresar']

        frame_cart, self.cart_tree = make_treeview(right, cols, height=10)
        frame_cart.pack(fill=BOTH, expand=True)
        for col in cols:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=140, anchor='center')
        self.cart_tree.column('Descripción', width=200, anchor='w')

        tb.Button(right, text="🗑️ Quitar", bootstyle="danger-outline",
                  command=self._quitar_item).pack(anchor='w', pady=5)

        tk.Frame(right, bg='#eee', height=1).pack(fill=X, pady=6)

        if self.es_admin:
            self.lbl_total = tk.Label(right, text="TOTAL: Bs. 0.00",
                                       font=("Arial", 11, "bold"),
                                       bg='white', fg=HEADER_BG)
            self.lbl_total.pack(anchor='e', pady=(0,8))

        tb.Button(right,
                  text="✅ REGISTRAR COMPRA" if self.es_admin
                  else "✅ CONFIRMAR ENTRADA DE STOCK",
                  bootstyle="dark",
                  command=self._registrar).pack(ipadx=5, ipady=5)

        self._buscar_producto()

    def _build_historial_tab(self, parent):
        toolbar = tk.Frame(parent, bg=CONTENT_BG, pady=8, padx=10)
        toolbar.pack(fill=X)
        tb.Button(toolbar, text="🔄 Actualizar", bootstyle="secondary-outline",
                  command=self._load_historial).pack(side=LEFT)

        card = tk.Frame(parent, bg='white',
                        highlightbackground='#e0e0e0', highlightthickness=1)
        card.pack(fill=BOTH, expand=True, padx=10, pady=(0,10))

        if self.es_admin:
            cols = ['#', 'Fecha', 'Proveedor', 'Total']
            self._hist_keys = ['id', 'fecha', 'proveedor', 'total']
        else:
            cols = ['#', 'Fecha', 'Productos ingresados']
            self._hist_keys = ['id', 'fecha', 'proveedor']

        frame_tree, self.hist_tree = make_treeview(card, cols, height=18)
        frame_tree.pack(fill=BOTH, expand=True, padx=10, pady=8)
        widths = {'#': 60, 'Fecha': 140, 'Proveedor': 200,
                  'Total': 100, 'Productos ingresados': 250}
        for col in cols:
            self.hist_tree.heading(col, text=col)
            self.hist_tree.column(col, width=widths.get(col,100), anchor='center')
        if 'Proveedor' in cols or 'Productos ingresados' in cols:
            self.hist_tree.column(cols[2], anchor='w')
        self._compras_data = []

    def _load_historial(self):
        if not hasattr(self, 'hist_tree'): return
        self._compras_data = get_compras()
        rows = []
        for c in self._compras_data:
            r = dict(c)
            if self.es_admin:
                r['total'] = f"Bs. {c['total']:.2f}"
            rows.append(r)
        populate_tree(self.hist_tree, rows, self._hist_keys)

    def _buscar_producto(self, *args):
        self._productos_filtrados = get_productos(
            solo_activos=True, busqueda=self.busq_var.get())
        self.prod_listbox.delete(0, END)
        for p in self._productos_filtrados:
            cod = p.get('codigo_proveedor') or p.get('codigo_tienda') or ''
            self.prod_listbox.insert(
                END, f"{cod:<14} {p['descripcion'][:35]:<36} Stock:{p['stock']}")

    def _on_producto_select(self, event):
        sel = self.prod_listbox.curselection()
        if not sel: return
        p = self._producto_sel = self._productos_filtrados[sel[0]]
        info = f"📦 {p['descripcion']}  |  Stock actual: {p['stock']}"
        if self.es_admin:
            info += f"  |  Último costo: Bs.{p['precio_compra']:.2f}"
            self.costo_var.set(str(p['precio_compra']))
        self.info_label.config(text=info, fg='#1a1a2e')

    def _agregar_item(self):
        if not self._producto_sel:
            messagebox.showwarning("Atención", "Seleccione un producto", parent=self)
            return
        try:
            cant = int(self.cant_var.get())
            costo = float(self.costo_var.get()) if self.es_admin else 0
        except:
            messagebox.showwarning("Error", "Valores numéricos inválidos", parent=self)
            return
        if cant <= 0:
            messagebox.showwarning("Error", "La cantidad debe ser mayor a 0", parent=self)
            return
        if self.es_admin and costo <= 0:
            messagebox.showwarning("Error", "El costo debe ser mayor a 0", parent=self)
            return

        p = self._producto_sel
        # Verificar duplicado
        for item in self.items_compra:
            if item['producto_id'] == p['id']:
                item['cantidad'] += cant
                self._refresh_carrito()
                return

        self.items_compra.append({
            'producto_id':   p['id'],
            'descripcion':   p['descripcion'],
            'cantidad':      cant,
            'costo_unitario': costo,
        })
        self._refresh_carrito()
        self.cant_var.set('1')

    def _quitar_item(self):
        sel = self.cart_tree.selection()
        if sel:
            self.items_compra.pop(self.cart_tree.index(sel[0]))
            self._refresh_carrito()

    def _refresh_carrito(self):
        self.cart_tree.delete(*self.cart_tree.get_children())
        total_gral = 0
        for i, item in enumerate(self.items_compra):
            tag = 'odd' if i % 2 else 'even'
            if self.es_admin:
                total = item['cantidad'] * item['costo_unitario']
                total_gral += total
                self.cart_tree.insert('', END, values=(
                    item['descripcion'], item['cantidad'],
                    f"Bs.{item['costo_unitario']:.2f}",
                    f"Bs.{total:.2f}"), tags=(tag,))
            else:
                self.cart_tree.insert('', END, values=(
                    item['descripcion'], item['cantidad']), tags=(tag,))
        if self.es_admin:
            self.lbl_total.config(text=f"TOTAL: Bs. {total_gral:.2f}")

    def _registrar(self):
        if not self.items_compra:
            messagebox.showwarning("Atención", "Agregue productos", parent=self)
            return

        if self.es_admin:
            prov_nombre = self.prov_var.get()
            prov = next((p for p in self._proveedores
                         if p['nombre'] == prov_nombre), None)
            if not prov:
                messagebox.showwarning("Error", "Seleccione un proveedor", parent=self)
                return
            msg = (f"¿Registrar compra al proveedor {prov_nombre}?\n"
                   f"Se actualizarán stocks, precios de compra y venta.")
            if not messagebox.askyesno("Confirmar", msg, parent=self): return
            compra_id = registrar_compra(prov['id'], self.items_compra)
            messagebox.showinfo("✅ Éxito",
                                f"Compra #{compra_id} registrada.\n"
                                f"Stocks y precios actualizados.", parent=self)
        else:
            # Vendedor: solo suma stock, costo_unitario = 0 (no toca precios)
            resumen = "\n".join(f"  • {i['descripcion']}: +{i['cantidad']}"
                                for i in self.items_compra)
            if not messagebox.askyesno(
                    "Confirmar entrada de stock",
                    f"¿Confirmar entrada de stock?\n\n{resumen}", parent=self):
                return
            registrar_entrada_stock(self.items_compra)
            messagebox.showinfo("✅ Stock actualizado",
                                "Stock ingresado correctamente.", parent=self)

        self.items_compra.clear()
        self._refresh_carrito()
        self._buscar_producto()
        self._load_historial()
