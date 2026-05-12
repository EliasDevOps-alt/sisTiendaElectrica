import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
from views.base_view import *
from controllers.controller import *

# ═══════════════════════════════════════════
# CLIENTES VIEW
# ═══════════════════════════════════════════
class ClientesView(tk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent, bg=CONTENT_BG)
        self.usuario = usuario
        self.busq_var = tk.StringVar()
        self._data = []
        self._build()
        self._load()

    def _build(self):
        make_page_header(self, "👤 Clientes", "Gestión de clientes").pack(fill=X)
        toolbar = tk.Frame(self, bg=CONTENT_BG, padx=15, pady=10)
        toolbar.pack(fill=X)
        make_search_bar(toolbar, self.busq_var, self._load).pack(side=LEFT)
        tb.Button(toolbar, text="+ Nuevo Cliente", bootstyle="dark", command=self._nuevo).pack(side=RIGHT)

        card = make_card(self)
        cols = ['#', 'Nombre', 'Celular', 'CI/NIT', 'Categoría', 'Descuento Cat.']
        keys = ['id', 'nombre', 'celular', 'ci_nit', 'categoria', 'descuento_cat']
        self._keys = keys
        frame_tree, self.tree = make_treeview(card, cols)
        frame_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        widths = {'#': 50, 'Nombre': 180, 'Celular': 100, 'CI/NIT': 100, 'Categoría': 120, 'Descuento Cat.': 100}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths.get(col, 100), anchor='center')
        self.tree.column('Nombre', anchor='w')
        self.tree.bind("<Double-1>", lambda e: self._editar())
        btn_frame = tk.Frame(card, bg='white', pady=8)
        btn_frame.pack(fill=X, padx=10)
        tb.Button(btn_frame, text="✏️ Editar", bootstyle="secondary-outline", command=self._editar).pack(side=LEFT, padx=3)

    def _load(self, *args):
        busq = self.busq_var.get().lower()
        self._data = [c for c in get_clientes() if busq in c['nombre'].lower()] if busq else get_clientes()
        rows = []
        for c in self._data:
            r = dict(c)
            r['descuento_cat'] = f"{c.get('descuento_cat',0):.1f}%"
            rows.append(r)
        populate_tree(self.tree, rows, self._keys)

    def _get_sel(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Atención", "Seleccione un cliente", parent=self); return None
        return self._data[self.tree.index(sel[0])]

    def _nuevo(self): ClienteDialog(self, None, self._load)
    def _editar(self):
        c = self._get_sel()
        if c: ClienteDialog(self, c, self._load)


class ClienteDialog(tk.Toplevel):
    def __init__(self, parent, cliente, callback):
        super().__init__(parent)
        self.cliente = cliente
        self.callback = callback
        self.title("Nuevo Cliente" if not cliente else "Editar Cliente")
        self.resizable(False, False); self.grab_set()
        self.configure(bg='white')
        w, h = 450, 360
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=HEADER_BG, padx=20, pady=12)
        hdr.pack(fill=X)
        tk.Label(hdr, text="Datos del Cliente", font=("Arial", 12, "bold"), bg=HEADER_BG, fg='white').pack(anchor='w')
        form = tk.Frame(self, bg='white', padx=20, pady=15)
        form.pack(fill=BOTH, expand=True)
        form.columnconfigure(1, weight=1)

        self._nombre = tk.StringVar()
        self._celular = tk.StringVar()
        self._ci_nit = tk.StringVar()
        self._cat = tk.StringVar()

        cats = get_categorias_clientes()
        self._cats = cats
        cat_names = [c['nombre'] for c in cats]

        rows_fields = [("Nombre *", self._nombre, False, None),
                       ("Celular", self._celular, False, None),
                       ("CI / NIT", self._ci_nit, False, None),
                       ("Categoría", self._cat, True, cat_names)]

        for i, (lbl, var, combo, vals) in enumerate(rows_fields):
            tk.Label(form, text=lbl, font=("Arial", 9, "bold"), bg='white', fg='#555').grid(row=i, column=0, sticky='w', padx=5, pady=6)
            if combo:
                w = tb.Combobox(form, textvariable=var, values=vals, state='readonly', width=28, font=("Arial", 9))
            else:
                w = tb.Entry(form, textvariable=var, width=30, font=("Arial", 9))
            w.grid(row=i, column=1, sticky='ew', padx=5)

        if cat_names: self._cat.set(cat_names[0])
        if self.cliente:
            self._nombre.set(self.cliente.get('nombre',''))
            self._celular.set(self.cliente.get('celular',''))
            self._ci_nit.set(self.cliente.get('ci_nit',''))
            cat_obj = next((c for c in cats if c['id'] == self.cliente.get('categoria_cliente_id')), None)
            if cat_obj: self._cat.set(cat_obj['nombre'])

        btn_frame = tk.Frame(self, bg='white', pady=10)
        btn_frame.pack(fill=X, padx=20)
        tb.Button(btn_frame, text="💾 Guardar", bootstyle="dark", command=self._guardar).pack(side=RIGHT, padx=5)
        tb.Button(btn_frame, text="Cancelar", bootstyle="secondary-outline", command=self.destroy).pack(side=RIGHT)

    def _guardar(self):
        if not self._nombre.get().strip():
            messagebox.showwarning("Error", "El nombre es obligatorio", parent=self); return
        cat = next((c for c in self._cats if c['nombre'] == self._cat.get()), None)
        data = {'nombre': self._nombre.get(), 'celular': self._celular.get(),
                'ci_nit': self._ci_nit.get(), 'categoria_cliente_id': cat['id'] if cat else None}
        save_cliente(data, self.cliente['id'] if self.cliente else None)
        self.callback(); self.destroy()


# ═══════════════════════════════════════════
# PROVEEDORES VIEW
# ═══════════════════════════════════════════
class ProveedoresView(tk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent, bg=CONTENT_BG)
        self.usuario = usuario
        self._data = []
        self._build(); self._load()

    def _build(self):
        make_page_header(self, "🚚 Proveedores", "Gestión de proveedores").pack(fill=X)
        toolbar = tk.Frame(self, bg=CONTENT_BG, padx=15, pady=10)
        toolbar.pack(fill=X)
        tb.Button(toolbar, text="+ Nuevo Proveedor", bootstyle="dark", command=self._nuevo).pack(side=RIGHT)

        card = make_card(self)
        cols = ['#', 'Nombre', 'Celular', 'Dirección', 'Desc.%']
        self._keys = ['id', 'nombre', 'celular', 'direccion', 'porcentaje_descuento']
        frame_tree, self.tree = make_treeview(card, cols)
        frame_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        widths = {'#': 50, 'Nombre': 180, 'Celular': 100, 'Dirección': 200, 'Desc.%': 70}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths.get(col, 100), anchor='center')
        self.tree.column('Nombre', anchor='w'); self.tree.column('Dirección', anchor='w')
        self.tree.bind("<Double-1>", lambda e: self._editar())
        btn_frame = tk.Frame(card, bg='white', pady=8)
        btn_frame.pack(fill=X, padx=10)
        tb.Button(btn_frame, text="✏️ Editar", bootstyle="secondary-outline", command=self._editar).pack(side=LEFT, padx=3)

    def _load(self):
        self._data = get_proveedores()
        rows = [dict(p) for p in self._data]
        populate_tree(self.tree, rows, self._keys)

    def _get_sel(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Atención", "Seleccione un proveedor", parent=self); return None
        return self._data[self.tree.index(sel[0])]

    def _nuevo(self): ProveedorDialog(self, None, self._load)
    def _editar(self):
        p = self._get_sel()
        if p: ProveedorDialog(self, p, self._load)


class ProveedorDialog(tk.Toplevel):
    def __init__(self, parent, proveedor, callback):
        super().__init__(parent)
        self.prov = proveedor; self.callback = callback
        self.title("Nuevo Proveedor" if not proveedor else "Editar Proveedor")
        self.resizable(False, False); self.grab_set(); self.configure(bg='white')
        w, h = 420, 340
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=HEADER_BG, padx=20, pady=12)
        hdr.pack(fill=X)
        tk.Label(hdr, text="Datos del Proveedor", font=("Arial", 12, "bold"), bg=HEADER_BG, fg='white').pack(anchor='w')
        form = tk.Frame(self, bg='white', padx=20, pady=15)
        form.pack(fill=BOTH, expand=True)
        form.columnconfigure(1, weight=1)

        self._vars = {k: tk.StringVar() for k in ['nombre', 'celular', 'direccion', 'porcentaje_descuento']}
        fields = [("Nombre *", 'nombre'), ("Celular", 'celular'), ("Dirección", 'direccion'), ("Desc. % (info)", 'porcentaje_descuento')]
        for i, (lbl, key) in enumerate(fields):
            tk.Label(form, text=lbl, font=("Arial", 9, "bold"), bg='white', fg='#555').grid(row=i, column=0, sticky='w', padx=5, pady=6)
            tb.Entry(form, textvariable=self._vars[key], width=28, font=("Arial", 9)).grid(row=i, column=1, sticky='ew', padx=5)

        self._vars['porcentaje_descuento'].set('0')
        if self.prov:
            for k in self._vars: self._vars[k].set(str(self.prov.get(k, '')))

        btn_frame = tk.Frame(self, bg='white', pady=10)
        btn_frame.pack(fill=X, padx=20)
        tb.Button(btn_frame, text="💾 Guardar", bootstyle="dark", command=self._guardar).pack(side=RIGHT, padx=5)
        tb.Button(btn_frame, text="Cancelar", bootstyle="secondary-outline", command=self.destroy).pack(side=RIGHT)

    def _guardar(self):
        if not self._vars['nombre'].get().strip():
            messagebox.showwarning("Error", "Nombre obligatorio", parent=self); return
        try: desc = float(self._vars['porcentaje_descuento'].get())
        except: desc = 0
        data = {'nombre': self._vars['nombre'].get(), 'celular': self._vars['celular'].get(),
                'direccion': self._vars['direccion'].get(), 'porcentaje_descuento': desc}
        save_proveedor(data, self.prov['id'] if self.prov else None)
        self.callback(); self.destroy()
