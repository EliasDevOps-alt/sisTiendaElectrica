import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
from views.base_view import *
from controllers.controller import *

class ProductosView(tk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent, bg=CONTENT_BG)
        self.usuario  = usuario
        self.es_admin = usuario['rol'] == 'ADMIN'
        self.busqueda_var = tk.StringVar()
        self.cat_var  = tk.StringVar(value="Todas")
        self.productos = []
        self._build()
        self._load()

    def _build(self):
        make_page_header(self, "🏷️ Productos",
                         "Gestión del catálogo de productos").pack(fill=X)

        # Toolbar
        toolbar = tk.Frame(self, bg=CONTENT_BG, padx=15, pady=8)
        toolbar.pack(fill=X)

        make_search_bar(toolbar, self.busqueda_var, self._load).pack(side=LEFT)

        # Filtro categoría
        cats = ["Todas"] + [c['nombre'] for c in get_categorias()]
        tb.Combobox(toolbar, textvariable=self.cat_var, values=cats,
                    state='readonly', width=15,
                    font=("Arial",9)).pack(side=LEFT, padx=(12,0))
        self.cat_var.trace('w', lambda *a: self._load())

        # Botón nuevo — disponible para ADMIN y VENDEDOR
        tb.Button(toolbar, text="+ Nuevo Producto", bootstyle="dark",
                  command=self._nuevo).pack(side=RIGHT, padx=5)

        # Columnas — precio_compra y % solo para ADMIN
        # Vendedor NO ve Desc.Máximo
        # Se agrega columna '#' para numeración ordenada por código de tienda
        if self.es_admin:
            cols = ['#','Cód.Prod','Cód.Tienda','Descripción','Categoría','Marca','UM',
                    'Stock','P.Compra','%Venta','P.Venta','Desc.Máx','Estado']
            self._col_keys = ['_num','codigo_proveedor','codigo_tienda','descripcion','categoria','marca',
                              'unidad_medida','stock','_pc','_pv_pct',
                              '_pv','_dm','_activo']
        else:
            cols = ['#','Cód.Prod','Cód.Tienda','Descripción','Categoría','Marca','UM',
                    'Stock','P.Venta','Estado']
            self._col_keys = ['_num','codigo_proveedor','codigo_tienda','descripcion','categoria','marca',
                              'unidad_medida','stock','_pv','_activo']

        card = make_card(self)
        frame_tree, self.tree = make_treeview(card, cols)
        frame_tree.pack(fill=BOTH, expand=True, padx=10, pady=8)

        w = {'#':40,'Cód.Prod':70,'Cód.Tienda':75,'Descripción':500,'Categoría':95,'Marca':85,'UM':55,
             'Stock':55,'P.Compra':80,'%Venta':60,'P.Venta':80,
             'Desc.Máx':70,'Estado':65}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w.get(col,80), anchor='center')
        self.tree.column('Descripción', anchor='w')

        self.tree.bind("<Double-1>", lambda e: self._editar())
        btn_frame = tk.Frame(card, bg='white', pady=6)
        btn_frame.pack(fill=X, padx=10)
        tb.Button(btn_frame, text="✏️ Editar", bootstyle="secondary-outline",
                  command=self._editar).pack(side=LEFT, padx=3)
        if self.es_admin:
            tb.Button(btn_frame, text="🔄 Activar/Desactivar",
                      bootstyle="warning-outline",
                      command=self._toggle_activo).pack(side=LEFT, padx=3)

    def _load(self, *args):
        busq    = self.busqueda_var.get()
        cat_nom = self.cat_var.get()
        cat_id  = None
        if cat_nom != "Todas":
            for c in get_categorias():
                if c['nombre'] == cat_nom:
                    cat_id = c['id']; break

        self.productos = get_productos(solo_activos=False, busqueda=busq,
                                       categoria_id=cat_id)
        
        # 📍 ORDENAR PRODUCTOS POR CÓDIGO DE TIENDA
        self.productos.sort(key=lambda p: p.get('codigo_tienda', ''))
        
        rows = []
        # 📍 AGREGAR NUMERACIÓN SECUENCIAL (1, 2, 3...)
        for idx, p in enumerate(self.productos, 1):
            r = dict(p)
            r['_num']    = str(idx)  # Número secuencial
            r['_activo'] = "✅ Activo" if p['activo'] else "❌ Inactivo"
            r['_pv']     = f"Bs.{p['precio_venta']:.2f}"
            r['_dm']     = f"{p['descuento_maximo']:.1f}%"
            if self.es_admin:
                r['_pc']     = f"Bs.{p['precio_compra']:.2f}"
                r['_pv_pct'] = f"{p['porcentaje_venta']:.1f}%"
            rows.append(r)
        populate_tree(self.tree, rows, self._col_keys)

    def _get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un producto", parent=self)
            return None
        return self.productos[self.tree.index(sel[0])]

    def _nuevo(self):
        ProductoDialog(self, None, self.es_admin, self._load)

    def _editar(self):
        p = self._get_selected()
        if p:
            ProductoDialog(self, p['id'], self.es_admin, self._load)

    def _toggle_activo(self):
        p = self._get_selected()
        if p:
            nuevo = 0 if p['activo'] else 1
            msg   = "activar" if nuevo else "desactivar"
            if messagebox.askyesno("Confirmar",
                                   f"¿Desea {msg} este producto?", parent=self):
                toggle_producto_activo(p['id'], nuevo)
                self._load()


# ── Diálogo Producto ─────────────────────────────────────────────
class ProductoDialog(tk.Toplevel):
    def __init__(self, parent, producto_id, es_admin, callback):
        super().__init__(parent)
        self.producto_id = producto_id
        self.es_admin    = es_admin
        self.callback    = callback
        self.title("Nuevo Producto" if not producto_id else "Editar Producto")
        self.resizable(False, False)
        self.grab_set()
        self.configure(bg='white')

        # Altura según rol: admin ve más campos, vendedor ahora también puede editar stock
        h = 520 if es_admin else 470
        w = 560
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        self._vars = {}
        self._build()
        if producto_id:
            self._load_data()

    def _build(self):
        hdr = tk.Frame(self, bg=HEADER_BG, padx=20, pady=10)
        hdr.pack(fill=X)
        tk.Label(hdr, text="Datos del Producto", font=("Arial", 11, "bold"),
                 bg=HEADER_BG, fg='white').pack(anchor='w')

        form = tk.Frame(self, bg='white', padx=12, pady=10)
        form.pack(fill=BOTH, expand=True)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        categorias = get_categorias()
        marcas     = get_marcas()
        cat_names  = [c['nombre'] for c in categorias]
        mar_names  = [m['nombre'] for m in marcas]
        self._categorias = categorias
        self._marcas     = marcas

        # Campos comunes (visible para todos)
        comunes = [
            ('Cód. Proveedor', 'codigo_proveedor', 0, 0, False, None),
            ('Descripción',    'descripcion',       1, 0, False, None),
            ('Categoría',      'categoria_id',      2, 0, True,  cat_names),
            ('Marca',          'marca_id',           3, 0, True,  mar_names),
            ('Unidad Medida',  'unidad_medida',      4, 0, False, None),
        ]

        # Campos exclusivos ADMIN
        admin_fields = [
            ('Precio Compra',  'precio_compra',    0, 1, False, None),
            ('% Venta',        'porcentaje_venta', 1, 1, False, None),
            ('Precio Venta',   'precio_venta',     2, 1, False, None),
            ('Desc. Máximo %', 'descuento_maximo', 3, 1, False, None),
            ('Stock inicial',  'stock',            4, 1, False, None),
        ]

        # Campos para VENDEDOR (precio venta, descuento máximo y stock)
        vendedor_fields = [
            ('Precio Venta',   'precio_venta',    0, 1, False, None),
            ('Desc. Máximo %', 'descuento_maximo',1, 1, False, None),
            ('Stock inicial',  'stock',           2, 1, False, None),
        ]

        all_fields = comunes + (admin_fields if self.es_admin else vendedor_fields)

        for label, key, row, col, is_combo, vals in all_fields:
            self._vars[key] = tk.StringVar()
            # precio_venta y descuento_maximo son de solo lectura para vendedor
            readonly = (not self.es_admin and
                        key in ('precio_venta', 'descuento_maximo'))
            w = form_field(form, label, row, col,
                           is_combo=is_combo, values=vals,
                           textvariable=self._vars[key], width=18,
                           state='readonly' if (is_combo or readonly) else 'normal')
        
        # Agregar campo stock para vendedor (editable)
        if not self.es_admin and 'stock' not in self._vars:
            self._vars['stock'] = tk.StringVar()

        # Defaults
        self._vars['unidad_medida'].set('UNIDAD')
        if self.es_admin:
            self._vars['stock'].set('0')
            self._vars['precio_compra'].set('0')
            self._vars['porcentaje_venta'].set('0')
            self._vars['precio_venta'].set('0')
            self._vars['descuento_maximo'].set('0')
            self._vars['precio_compra'].trace('w', self._calc_pv)
            self._vars['porcentaje_venta'].trace('w', self._calc_pv)
        else:
            self._vars['precio_venta'].set('0')
            self._vars['descuento_maximo'].set('0')
            self._vars['stock'].set('0')

        if cat_names: self._vars['categoria_id'].set(cat_names[0])
        if mar_names: self._vars['marca_id'].set(mar_names[0])

        # Si es vendedor: aviso
        if not self.es_admin:
            tk.Label(form, text="ℹ️  Precio y descuento son asignados por Administración. Tú puedes gestionar el stock.",
                     font=("Arial", 8), bg='white', fg='#888',
                     wraplength=340, justify='left').grid(
                     row=3, column=2, columnspan=2, sticky='w', padx=8, pady=4)

        # Botones
        btn_frame = tk.Frame(self, bg='white', pady=8)
        btn_frame.pack(fill=X, padx=20)
        tb.Button(btn_frame, text="💾 Guardar", bootstyle="dark",
                  command=self._guardar).pack(side=RIGHT, padx=5)
        tb.Button(btn_frame, text="Cancelar", bootstyle="secondary-outline",
                  command=self.destroy).pack(side=RIGHT)

    def _calc_pv(self, *args):
        try:
            c   = float(self._vars['precio_compra'].get())
            pct = float(self._vars['porcentaje_venta'].get())
            self._vars['precio_venta'].set(str(round(c + c * pct / 100, 2)))
        except: pass

    def _load_data(self):
        p = get_producto_by_id(self.producto_id)
        if not p: return
        self._vars['codigo_proveedor'].set(p.get('codigo_proveedor') or '')
        self._vars['descripcion'].set(p.get('descripcion') or '')
        self._vars['unidad_medida'].set(p.get('unidad_medida') or 'UNIDAD')
        self._vars['precio_venta'].set(str(p.get('precio_venta', 0)))
        self._vars['descuento_maximo'].set(str(p.get('descuento_maximo', 0)))
        self._vars['stock'].set(str(p.get('stock', 0)))  # Stock para admin y vendedor
        if self.es_admin:
            self._vars['precio_compra'].set(str(p.get('precio_compra', 0)))
            self._vars['porcentaje_venta'].set(str(p.get('porcentaje_venta', 0)))
        for c in self._categorias:
            if c['id'] == p.get('categoria_id'):
                self._vars['categoria_id'].set(c['nombre']); break
        for m in self._marcas:
            if m['id'] == p.get('marca_id'):
                self._vars['marca_id'].set(m['nombre']); break

    def _guardar(self):
        desc = self._vars['descripcion'].get().strip()
        if not desc:
            messagebox.showwarning("Error", "La descripción es obligatoria",
                                   parent=self); return
        try:
            precio_venta   = float(self._vars['precio_venta'].get())
            descuento_max  = float(self._vars['descuento_maximo'].get())
            precio_compra  = float(self._vars.get('precio_compra',
                                   tk.StringVar(value='0')).get()
                                   if self.es_admin else 0)
            porcentaje     = float(self._vars.get('porcentaje_venta',
                                   tk.StringVar(value='0')).get()
                                   if self.es_admin else 0)
            stock          = int(self._vars['stock'].get())  # Stock para admin y vendedor
        except ValueError:
            messagebox.showwarning("Error", "Los campos numéricos deben ser válidos",
                                   parent=self); return

        cat_nom = self._vars['categoria_id'].get()
        mar_nom = self._vars['marca_id'].get()
        cat_id  = next((c['id'] for c in self._categorias
                        if c['nombre'] == cat_nom), None)
        mar_id  = next((m['id'] for m in self._marcas
                        if m['nombre'] == mar_nom), None)

        data = {
            'codigo_proveedor': self._vars['codigo_proveedor'].get(),
            'descripcion':      desc,
            'categoria_id':     cat_id,
            'marca_id':         mar_id,
            'unidad_medida':    self._vars['unidad_medida'].get(),
            'precio_compra':    precio_compra,
            'porcentaje_venta': porcentaje,
            'precio_venta':     precio_venta,
            'descuento_maximo': descuento_max,
            'stock':            stock,
            'activo':           1,
        }
        save_producto(data, self.producto_id)
        self.callback()
        self.destroy()