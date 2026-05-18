import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
from views.base_view import *
from controllers.controller import *

# ═══════════════════════════════════════════
# CAJA VIEW
# ═══════════════════════════════════════════
class CajaView(tk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent, bg=CONTENT_BG)
        self.usuario = usuario
        self._data = []
        self._build(); self._load()

    def _build(self):
        make_page_header(self, "💰 Caja", "Movimientos de ingresos y egresos").pack(fill=X)

        # Stats
        self.stats_frame = tk.Frame(self, bg=CONTENT_BG, padx=15, pady=10)
        self.stats_frame.pack(fill=X)
        self.lbl_ing = stat_card(self.stats_frame, "INGRESOS TOTALES", "Bs. 0.00", '#4CAF50', '⬆')
        self.lbl_ing.pack(side=LEFT, fill=BOTH, expand=True, padx=(0,8))
        self.lbl_egr = stat_card(self.stats_frame, "EGRESOS TOTALES", "Bs. 0.00", '#F44336', '⬇')
        self.lbl_egr.pack(side=LEFT, fill=BOTH, expand=True, padx=(0,8))
        self.lbl_sal = stat_card(self.stats_frame, "SALDO", "Bs. 0.00", '#1a1a2e', '💰')
        self.lbl_sal.pack(side=LEFT, fill=BOTH, expand=True)

        # Toolbar
        toolbar = tk.Frame(self, bg=CONTENT_BG, padx=15, pady=5)
        toolbar.pack(fill=X)
        tb.Button(toolbar, text="+ Movimiento Manual", bootstyle="dark",
                  command=self._nuevo_movimiento).pack(side=LEFT)
        tb.Button(toolbar, text="🔄 Actualizar", bootstyle="secondary-outline",
                  command=self._load).pack(side=LEFT, padx=5)

        card = make_card(self)
        cols = ['#', 'Tipo', 'Monto', 'Descripción', 'Fecha']
        self._keys = ['id', 'tipo', 'monto', 'descripcion', 'fecha']
        frame_tree, self.tree = make_treeview(card, cols, height=18)
        frame_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        widths = {'#': 60, 'Tipo': 80, 'Monto': 100, 'Descripción': 250, 'Fecha': 140}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths.get(col, 100), anchor='center')
        self.tree.column('Descripción', anchor='w')
        self.tree.tag_configure('ingreso', foreground='#4CAF50')
        self.tree.tag_configure('egreso', foreground='#F44336')

    def _load(self):
        self._data = get_movimientos_caja()
        resumen = get_resumen_caja()
        # Actualizar stats
        for w in self.stats_frame.winfo_children(): w.destroy()
        stat_card(self.stats_frame, "INGRESOS TOTALES", f"Bs. {resumen['ingresos']:.2f}", '#4CAF50', '⬆').pack(side=LEFT, fill=BOTH, expand=True, padx=(0,8))
        stat_card(self.stats_frame, "EGRESOS TOTALES", f"Bs. {resumen['egresos']:.2f}", '#F44336', '⬇').pack(side=LEFT, fill=BOTH, expand=True, padx=(0,8))
        color_saldo = '#4CAF50' if resumen['saldo'] >= 0 else '#F44336'
        stat_card(self.stats_frame, "SALDO", f"Bs. {resumen['saldo']:.2f}", color_saldo, '💰').pack(side=LEFT, fill=BOTH, expand=True)

        self.tree.delete(*self.tree.get_children())
        for i, mov in enumerate(self._data):
            tag = 'ingreso' if mov['tipo'] == 'INGRESO' else 'egreso'
            tipo_label = '⬆ INGRESO' if mov['tipo'] == 'INGRESO' else '⬇ EGRESO'
            self.tree.insert('', END, values=(
                mov['id'], tipo_label, f"Bs. {mov['monto']:.2f}",
                mov.get('descripcion', ''), mov.get('fecha', '')
            ), tags=(tag,))

    def _nuevo_movimiento(self):
        top = tk.Toplevel(self)
        top.title("Movimiento Manual")
        top.resizable(False, False); top.grab_set(); top.configure(bg='white')
        top.geometry(f"380x260+{(top.winfo_screenwidth()-380)//2}+{(top.winfo_screenheight()-260)//2}")

        hdr = tk.Frame(top, bg=HEADER_BG, padx=20, pady=12)
        hdr.pack(fill=X)
        tk.Label(hdr, text="Registrar Movimiento", font=("Arial", 12, "bold"), bg=HEADER_BG, fg='white').pack(anchor='w')

        form = tk.Frame(top, bg='white', padx=20, pady=15)
        form.pack(fill=BOTH, expand=True)
        form.columnconfigure(1, weight=1)

        tipo_var = tk.StringVar(value='INGRESO')
        monto_var = tk.StringVar(value='0')
        desc_var = tk.StringVar()

        tk.Label(form, text="Tipo", font=("Arial", 9, "bold"), bg='white', fg='#555').grid(row=0, column=0, sticky='w', padx=5, pady=6)
        frame_tipo = tk.Frame(form, bg='white')
        frame_tipo.grid(row=0, column=1, sticky='w')
        tb.Radiobutton(frame_tipo, text="Ingreso", variable=tipo_var, value='INGRESO', bootstyle="success").pack(side=LEFT)
        tb.Radiobutton(frame_tipo, text="Egreso", variable=tipo_var, value='EGRESO', bootstyle="danger").pack(side=LEFT, padx=10)

        tk.Label(form, text="Monto Bs.", font=("Arial", 9, "bold"), bg='white', fg='#555').grid(row=1, column=0, sticky='w', padx=5, pady=6)
        tb.Entry(form, textvariable=monto_var, width=20).grid(row=1, column=1, sticky='ew', padx=5)

        tk.Label(form, text="Descripción", font=("Arial", 9, "bold"), bg='white', fg='#555').grid(row=2, column=0, sticky='w', padx=5, pady=6)
        tb.Entry(form, textvariable=desc_var, width=28).grid(row=2, column=1, sticky='ew', padx=5)

        def guardar():
            try: monto = float(monto_var.get())
            except: messagebox.showwarning("Error", "Monto inválido", parent=top); return
            registrar_movimiento_manual(tipo_var.get(), monto, desc_var.get())
            self._load(); top.destroy()

        btn_frame = tk.Frame(top, bg='white', pady=10)
        btn_frame.pack(fill=X, padx=20)
        tb.Button(btn_frame, text="💾 Guardar", bootstyle="dark", command=guardar).pack(side=RIGHT, padx=5)
        tb.Button(btn_frame, text="Cancelar", bootstyle="secondary-outline", command=top.destroy).pack(side=RIGHT)


# ═══════════════════════════════════════════
# INVENTARIO VIEW
# ═══════════════════════════════════════════
class InventarioView(tk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent, bg=CONTENT_BG)
        self.usuario = usuario
        self._build(); self._load()

    def _build(self):
        make_page_header(self, "📊 Inventario", "Valor del inventario y análisis de ganancias").pack(fill=X)

        # Stats
        self.stats_frame = tk.Frame(self, bg=CONTENT_BG, padx=15, pady=10)
        self.stats_frame.pack(fill=X)

        toolbar = tk.Frame(self, bg=CONTENT_BG, padx=15, pady=5)
        toolbar.pack(fill=X)
        tb.Button(toolbar, text="🔄 Actualizar", bootstyle="secondary-outline", command=self._load).pack(side=LEFT)
        tb.Button(toolbar, text="⚠️ Stock Bajo", bootstyle="warning-outline", command=self._show_stock_bajo).pack(side=LEFT, padx=5)

        card = make_card(self)
        cols = ['#','Código','Descripción','Stock','P.Compra','P.Venta','Val.Inventario','Gan.Unit.','Gan.Total']
        self._keys = ['_num','codigo_tienda','descripcion','stock','precio_compra','precio_venta',
                      'valor_inventario','ganancia_unitaria','ganancia_total']
        frame_tree, self.tree = make_treeview(card, cols, height=18)
        frame_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        widths = {'#': 40, 'Código': 80, 'Descripción': 200, 'Stock': 60, 'P.Compra': 90, 'P.Venta': 90,
                  'Val.Inventario': 110, 'Gan.Unit.': 90, 'Gan.Total': 100}
        for col in cols:
            self.tree.heading(col, text=col, command=lambda c=col: None)
            self.tree.column(col, width=widths.get(col, 90), anchor='center')
        self.tree.column('Descripción', anchor='w')

    def _load(self):
        data = get_valor_inventario()
        
        # 📍 ORDENAR POR CÓDIGO DE TIENDA
        data.sort(key=lambda r: r.get('codigo_tienda', ''))
        
        # Stats
        for w in self.stats_frame.winfo_children(): w.destroy()
        total_inv = sum(r['valor_inventario'] for r in data)
        total_gan = sum(r['ganancia_total'] for r in data)
        total_prod = len(data)
        stat_card(self.stats_frame, "PRODUCTOS ACTIVOS", str(total_prod), '#1a1a2e', '📦').pack(side=LEFT, fill=BOTH, expand=True, padx=(0,8))
        stat_card(self.stats_frame, "VALOR INVENTARIO", f"Bs. {total_inv:,.2f}", '#0f3460', '💼').pack(side=LEFT, fill=BOTH, expand=True, padx=(0,8))
        stat_card(self.stats_frame, "GANANCIA POTENCIAL", f"Bs. {total_gan:,.2f}", '#4CAF50', '📈').pack(side=LEFT, fill=BOTH, expand=True)

        rows = []
        # 📍 AGREGAR NUMERACIÓN SECUENCIAL (1, 2, 3...)
        for idx, r in enumerate(data, 1):
            row = dict(r)
            row['_num'] = str(idx)  # Número secuencial
            row['precio_compra'] = f"Bs.{r['precio_compra']:.2f}"
            row['precio_venta'] = f"Bs.{r['precio_venta']:.2f}"
            row['valor_inventario'] = f"Bs.{r['valor_inventario']:.2f}"
            row['ganancia_unitaria'] = f"Bs.{r['ganancia_unitaria']:.2f}"
            row['ganancia_total'] = f"Bs.{r['ganancia_total']:.2f}"
            rows.append(row)
        populate_tree(self.tree, rows, self._keys)

    def _show_stock_bajo(self):
        bajo = get_stock_bajo(5)
        if not bajo:
            messagebox.showinfo("✅ Stock OK", "Todos los productos tienen stock suficiente (>5)", parent=self); return
        msg = "⚠️ Productos con stock bajo (≤5):\n\n"
        for p in bajo:
            msg += f"• [{p['codigo_tienda']}] {p['descripcion']}: {p['stock']} unidades\n"
        messagebox.showwarning("Stock Bajo", msg, parent=self)


# ═══════════════════════════════════════════
# USUARIOS VIEW
# ═══════════════════════════════════════════
class UsuariosView(tk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent, bg=CONTENT_BG)
        self.usuario = usuario
        self._data = []
        self._build(); self._load()

    def _build(self):
        make_page_header(self, "⚙️ Usuarios", "Gestión de usuarios y roles").pack(fill=X)
        toolbar = tk.Frame(self, bg=CONTENT_BG, padx=15, pady=10)
        toolbar.pack(fill=X)
        tb.Button(toolbar, text="+ Nuevo Usuario", bootstyle="dark", command=self._nuevo).pack(side=RIGHT)

        card = make_card(self)
        cols = ['#', 'Nombre', 'Username', 'Rol']
        self._keys = ['id', 'nombre', 'username', 'rol']
        frame_tree, self.tree = make_treeview(card, cols, height=15)
        frame_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        widths = {'#': 60, 'Nombre': 200, 'Username': 150, 'Rol': 100}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths.get(col, 100), anchor='center')
        self.tree.column('Nombre', anchor='w')
        self.tree.bind("<Double-1>", lambda e: self._editar())
        btn_frame = tk.Frame(card, bg='white', pady=8)
        btn_frame.pack(fill=X, padx=10)
        tb.Button(btn_frame, text="✏️ Editar", bootstyle="secondary-outline", command=self._editar).pack(side=LEFT, padx=3)

    def _load(self):
        self._data = get_usuarios()
        populate_tree(self.tree, self._data, self._keys)

    def _get_sel(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Atención", "Seleccione un usuario", parent=self); return None
        return self._data[self.tree.index(sel[0])]

    def _nuevo(self): UsuarioDialog(self, None, self._load)
    def _editar(self):
        u = self._get_sel()
        if u: UsuarioDialog(self, u, self._load)


class UsuarioDialog(tk.Toplevel):
    def __init__(self, parent, usuario, callback):
        super().__init__(parent)
        self.usr = usuario; self.callback = callback
        self.title("Nuevo Usuario" if not usuario else "Editar Usuario")
        self.resizable(False, False); self.grab_set(); self.configure(bg='white')
        w, h = 420, 360
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=HEADER_BG, padx=20, pady=12)
        hdr.pack(fill=X)
        tk.Label(hdr, text="Datos del Usuario", font=("Arial", 12, "bold"), bg=HEADER_BG, fg='white').pack(anchor='w')
        form = tk.Frame(self, bg='white', padx=20, pady=15)
        form.pack(fill=BOTH, expand=True)
        form.columnconfigure(1, weight=1)

        self._vars = {k: tk.StringVar() for k in ['nombre', 'username', 'password', 'rol']}
        self._vars['rol'].set('VENDEDOR')

        fields = [("Nombre *", 'nombre', False, None),
                  ("Username *", 'username', False, None),
                  ("Contraseña", 'password', False, None),
                  ("Rol *", 'rol', True, ['ADMIN', 'VENDEDOR'])]

        for i, (lbl, key, combo, vals) in enumerate(fields):
            tk.Label(form, text=lbl, font=("Arial", 9, "bold"), bg='white', fg='#555').grid(row=i, column=0, sticky='w', padx=5, pady=6)
            if combo:
                w = tb.Combobox(form, textvariable=self._vars[key], values=vals, state='readonly', width=28)
            else:
                show = '●' if key == 'password' else ''
                w = tb.Entry(form, textvariable=self._vars[key], width=30, show=show)
            w.grid(row=i, column=1, sticky='ew', padx=5)

        if self.usr:
            self._vars['nombre'].set(self.usr.get('nombre', ''))
            self._vars['username'].set(self.usr.get('username', ''))
            self._vars['rol'].set(self.usr.get('rol', 'VENDEDOR'))
            tk.Label(form, text="(Dejar vacío para no cambiar contraseña)", font=("Arial", 7), bg='white', fg='gray').grid(row=2, column=1, sticky='w', padx=5)

        btn_frame = tk.Frame(self, bg='white', pady=10)
        btn_frame.pack(fill=X, padx=20)
        tb.Button(btn_frame, text="💾 Guardar", bootstyle="dark", command=self._guardar).pack(side=RIGHT, padx=5)
        tb.Button(btn_frame, text="Cancelar", bootstyle="secondary-outline", command=self.destroy).pack(side=RIGHT)

    def _guardar(self):
        if not self._vars['nombre'].get().strip() or not self._vars['username'].get().strip():
            messagebox.showwarning("Error", "Nombre y username son obligatorios", parent=self); return
        data = {k: self._vars[k].get() for k in self._vars}
        save_usuario(data, self.usr['id'] if self.usr else None)
        self.callback(); self.destroy()


# ═══════════════════════════════════════════
# CATÁLOGOS VIEW (Categorías y Marcas)
# ═══════════════════════════════════════════
class CatalogosView(tk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent, bg=CONTENT_BG)
        self.usuario = usuario
        self._build()

    def _build(self):
        make_page_header(self, "📁 Catálogos", "Categorías, marcas y categorías de clientes").pack(fill=X)
        notebook = tb.Notebook(self, bootstyle="dark")
        notebook.pack(fill=BOTH, expand=True, padx=15, pady=10)

        tab1 = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(tab1, text="  📂 Categorías Productos  ")
        CatalogoSimple(tab1, "Categorías", get_categorias, save_categoria).pack(fill=BOTH, expand=True)

        tab2 = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(tab2, text="  🏷️ Marcas  ")
        CatalogoSimple(tab2, "Marcas", get_marcas, save_marca).pack(fill=BOTH, expand=True)

        tab3 = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(tab3, text="  👥 Categorías Clientes  ")
        CatalogoCategoriaCliente(tab3).pack(fill=BOTH, expand=True)


class CatalogoSimple(tk.Frame):
    def __init__(self, parent, titulo, fn_get, fn_save):
        super().__init__(parent, bg=CONTENT_BG)
        self.titulo = titulo
        self.fn_get = fn_get
        self.fn_save = fn_save
        self._data = []
        self._build(); self._load()

    def _build(self):
        toolbar = tk.Frame(self, bg=CONTENT_BG, padx=15, pady=10)
        toolbar.pack(fill=X)
        self.entry_var = tk.StringVar()
        tb.Entry(toolbar, textvariable=self.entry_var, width=30, font=("Arial", 10)).pack(side=LEFT, padx=(0,8), ipady=4)
        tb.Button(toolbar, text="+ Agregar", bootstyle="dark", command=self._nuevo).pack(side=LEFT)
        tb.Button(toolbar, text="✏️ Editar Sel.", bootstyle="secondary-outline", command=self._editar).pack(side=LEFT, padx=5)

        card = make_card(self)
        frame_tree, self.tree = make_treeview(card, ['#', self.titulo], height=15)
        frame_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.tree.heading('#', text='#'); self.tree.column('#', width=60, anchor='center')
        self.tree.heading(self.titulo, text=self.titulo); self.tree.column(self.titulo, width=300, anchor='w')

    def _load(self):
        self._data = self.fn_get()
        populate_tree(self.tree, self._data, ['id', 'nombre'])

    def _nuevo(self):
        nombre = self.entry_var.get().strip()
        if not nombre: messagebox.showwarning("Error", "Escriba un nombre", parent=self); return
        self.fn_save(nombre)
        self.entry_var.set(''); self._load()

    def _editar(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Atención", "Seleccione uno", parent=self); return
        item = self._data[self.tree.index(sel[0])]
        nuevo_nombre = self.entry_var.get().strip()
        if not nuevo_nombre: messagebox.showwarning("Error", "Escriba el nuevo nombre", parent=self); return
        self.fn_save(nuevo_nombre, item['id'])
        self.entry_var.set(''); self._load()


class CatalogoCategoriaCliente(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CONTENT_BG)
        self._data = []
        self._build(); self._load()

    def _build(self):
        toolbar = tk.Frame(self, bg=CONTENT_BG, padx=15, pady=10)
        toolbar.pack(fill=X)
        self.nombre_var = tk.StringVar()
        self.desc_var = tk.StringVar(value='0')
        tk.Label(toolbar, text="Nombre:", font=("Arial", 9, "bold"), bg=CONTENT_BG).pack(side=LEFT)
        tb.Entry(toolbar, textvariable=self.nombre_var, width=20).pack(side=LEFT, padx=5)
        tk.Label(toolbar, text="Desc.%:", font=("Arial", 9, "bold"), bg=CONTENT_BG).pack(side=LEFT)
        tb.Entry(toolbar, textvariable=self.desc_var, width=8).pack(side=LEFT, padx=5)
        tb.Button(toolbar, text="+ Agregar", bootstyle="dark", command=self._nuevo).pack(side=LEFT, padx=5)
        tb.Button(toolbar, text="✏️ Editar Sel.", bootstyle="secondary-outline", command=self._editar).pack(side=LEFT)

        card = make_card(self)
        frame_tree, self.tree = make_treeview(card, ['#', 'Categoría', 'Descuento %'], height=15)
        frame_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.tree.heading('#', text='#'); self.tree.column('#', width=60, anchor='center')
        self.tree.heading('Categoría', text='Categoría'); self.tree.column('Categoría', width=250, anchor='w')
        self.tree.heading('Descuento %', text='Descuento %'); self.tree.column('Descuento %', width=100, anchor='center')

    def _load(self):
        self._data = get_categorias_clientes()
        rows = [{'id': r['id'], 'nombre': r['nombre'], 'desc': f"{r['porcentaje_descuento_margen']:.1f}%"} for r in self._data]
        populate_tree(self.tree, rows, ['id', 'nombre', 'desc'])

    def _nuevo(self):
        nombre = self.nombre_var.get().strip()
        if not nombre: messagebox.showwarning("Error", "Nombre requerido", parent=self); return
        try: desc = float(self.desc_var.get())
        except: desc = 0
        save_categoria_cliente(nombre, desc)
        self.nombre_var.set(''); self.desc_var.set('0'); self._load()

    def _editar(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Atención", "Seleccione uno", parent=self); return
        item = self._data[self.tree.index(sel[0])]
        nombre = self.nombre_var.get().strip()
        if not nombre: messagebox.showwarning("Error", "Escriba el nombre", parent=self); return
        try: desc = float(self.desc_var.get())
        except: desc = 0
        save_categoria_cliente(nombre, desc, item['id'])
        self.nombre_var.set(''); self.desc_var.set('0'); self._load()
