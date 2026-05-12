import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox

from views.productos_view import ProductosView
from views.ventas_view import VentasView
from views.compras_view import ComprasView
from views.clientes_view import ClientesView
from views.proveedores_view import ProveedoresView
from views.cotizaciones_view import CotizacionesView
from views.caja_view import CajaView
from views.inventario_view import InventarioView
from views.usuarios_view import UsuariosView
from views.catalogos_view import CatalogosView

SIDEBAR_BG = "#ffffff"
SIDEBAR_FG = '#e0e0e0'
SIDEBAR_HOVER = "#f6f6f6"
SIDEBAR_ACTIVE = "#ffffff"
CONTENT_BG = '#f0f2f5'

class MainWindow(tk.Frame):
    """Ventana principal como Frame — se monta dentro de la root window existente."""

    @staticmethod
    def build_into(root, usuario):
        """Monta el sistema completo dentro de la ventana root ya existente."""
        instance = MainWindow(root, usuario)
        instance.pack(fill=BOTH, expand=True)
        instance._navigate('ventas')
        return instance

    def __init__(self, parent, usuario):
        super().__init__(parent)
        self.usuario = usuario
        self.es_admin = usuario['rol'] == 'ADMIN'
        self.current_view = None
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── SIDEBAR ──────────────────────────────────
        self.sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=190)
        self.sidebar.grid(row=0, column=0, sticky=NSEW)
        self.sidebar.grid_propagate(False)

        logo_frame = tk.Frame(self.sidebar, bg=SIDEBAR_BG, pady=10)
        logo_frame.pack(fill=X)
        tk.Label(logo_frame, text="🏪", font=("Arial", 22), bg=SIDEBAR_BG, fg='white').pack()
        tk.Label(logo_frame, text="SISTEMA VENTAS", font=("Arial", 9, "bold"),
                 bg=SIDEBAR_BG, fg='white').pack()
        tk.Label(logo_frame, text=f"{self.usuario['nombre']}", font=("Arial", 8),
                 bg=SIDEBAR_BG, fg='#888').pack()
        tk.Label(logo_frame, text=f"● {self.usuario['rol']}", font=("Arial", 7),
                 bg=SIDEBAR_BG, fg='#4CAF50' if self.es_admin else '#FF9800').pack()

        tk.Frame(self.sidebar, bg='#333', height=1).pack(fill=X, padx=15, pady=5)

        self.nav_buttons = {}
        for item in self._get_menus():
            self._add_nav_item(item)

        tk.Frame(self.sidebar, bg=SIDEBAR_BG).pack(fill=BOTH, expand=True)
        tk.Frame(self.sidebar, bg='#333', height=1).pack(fill=X, padx=15)
        self._add_nav_item({'key': '__logout__', 'label': '⏻  Cerrar Sesión', 'action': self._logout})

        # ── CONTENT AREA ─────────────────────────────
        self.content_frame = tk.Frame(self, bg=CONTENT_BG)
        self.content_frame.grid(row=0, column=1, sticky=NSEW)
        self.content_frame.grid_propagate(False)

    def _get_menus(self):
        compras_label = '📦  Compras' if self.es_admin else '📦  Entrada Stock'
        menus = [
            {'key': 'ventas',       'label': '🛒  Ventas'},
            {'key': 'cotizaciones', 'label': '📋  Cotizaciones'},
            {'key': 'compras',      'label': compras_label},
            {'key': 'productos',    'label': '🏷️  Productos'},
            {'key': 'clientes',     'label': '👤  Clientes'},
            {'key': 'catalogos',    'label': '📁  Catálogos'},
        ]
        if self.es_admin:
            menus += [
                {'key': 'proveedores', 'label': '🚚  Proveedores'},
                {'key': 'inventario',  'label': '📊  Inventario'},
                {'key': 'caja',        'label': '💰  Caja'},
                {'key': 'usuarios',    'label': '⚙️  Usuarios'},
            ]
        return menus

    def _add_nav_item(self, item):
        key    = item['key']
        label  = item['label']
        action = item.get('action', lambda k=key: self._navigate(k))

        btn = tk.Label(self.sidebar, text=label, font=("Arial", 9),
                       bg=SIDEBAR_BG, fg=SIDEBAR_FG,
                       anchor='w', padx=15, pady=7, cursor='hand2')
        btn.pack(fill=X)

        btn.bind("<Enter>",    lambda e, b=btn: b.config(bg=SIDEBAR_HOVER))
        btn.bind("<Leave>",    lambda e, b=btn, k=key: b.config(
                                   bg=SIDEBAR_ACTIVE if self.nav_buttons.get('_active') == k else SIDEBAR_BG))
        btn.bind("<Button-1>", lambda e, a=action: a())
        self.nav_buttons[key] = btn

    def _navigate(self, key):
        active = self.nav_buttons.get('_active')
        if active and active in self.nav_buttons:
            self.nav_buttons[active].config(bg=SIDEBAR_BG)

        self.nav_buttons['_active'] = key
        if key in self.nav_buttons:
            self.nav_buttons[key].config(bg=SIDEBAR_ACTIVE)

        for w in self.content_frame.winfo_children():
            w.destroy()

        views_map = {
            'ventas':        lambda: VentasView(self.content_frame, self.usuario),
            'cotizaciones':  lambda: CotizacionesView(self.content_frame, self.usuario),
            'compras':       lambda: ComprasView(self.content_frame, self.usuario),
            'productos':     lambda: ProductosView(self.content_frame, self.usuario),
            'clientes':      lambda: ClientesView(self.content_frame, self.usuario),
            'proveedores':   lambda: ProveedoresView(self.content_frame, self.usuario),
            'inventario':    lambda: InventarioView(self.content_frame, self.usuario),
            'caja':          lambda: CajaView(self.content_frame, self.usuario),
            'catalogos':     lambda: CatalogosView(self.content_frame, self.usuario),
            'usuarios':      lambda: UsuariosView(self.content_frame, self.usuario),
        }
        if key in views_map:
            views_map[key]().pack(fill=BOTH, expand=True)

    def _logout(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Desea cerrar sesión?", parent=self):
            # Destruir el frame principal y volver al login
            root = self.winfo_toplevel()
            for w in root.winfo_children():
                w.destroy()
            root.resizable(False, False)
            root.state('normal')
            # Re-importar y reconstruir login
            import main as m
            m._build_login(root)
