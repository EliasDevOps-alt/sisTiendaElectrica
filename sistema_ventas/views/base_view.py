import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import ttk

# Colores usados en el diseño general de las vistas
CONTENT_BG = '#f0f2f5'
CARD_BG = 'white'
HEADER_BG = '#1a1a2e'
ACCENT = '#0f3460'

# -----------------------------------------------------------------------------
# Componentes reutilizables para las pantallas
# -----------------------------------------------------------------------------

def make_page_header(parent, title, subtitle=""):
    """Crear una cabecera de página con título y subtítulo.

    parent: widget contenedor donde se coloca la cabecera.
    title: texto principal de la sección.
    subtitle: texto secundario opcional.
    """
    frame = tk.Frame(parent, bg=HEADER_BG, padx=20, pady=15)
    tk.Label(frame, text=title, font=("Arial", 16, "bold"),
             bg=HEADER_BG, fg='white').pack(anchor='w')
    if subtitle:
        tk.Label(frame, text=subtitle, font=("Arial", 9),
                 bg=HEADER_BG, fg='#aaa').pack(anchor='w')
    return frame


def make_card(parent, padx=15, pady=15):
    """Crear un contenedor tipo 'card' para agrupar secciones.

    Este cuadro tiene fondo blanco, borde ligero y relleno interno.
    """
    card = tk.Frame(parent, bg=CARD_BG, relief='flat', bd=0,
                    highlightbackground='#e0e0e0', highlightthickness=1)
    card.pack(fill=BOTH, expand=True, padx=padx, pady=pady)
    return card


def make_treeview(parent, columns, show='headings', height=15):
    """Crear un Treeview con estilo personalizado y barra de desplazamiento.

    parent: contenedor donde se agrega el Treeview.
    columns: lista de nombres de columnas para la tabla.
    show: indica si se muestran encabezados.
    height: número de filas visibles.

    Devuelve el frame contenedor y el widget Treeview.
    """
    frame = tk.Frame(parent, bg=CARD_BG)
    style = tb.Style()
    style.configure("Custom.Treeview",
                    background="white",
                    foreground="#333",
                    rowheight=26,
                    fieldbackground="white",
                    font=("Arial", 8))
    style.configure("Custom.Treeview.Heading",
                    background=HEADER_BG,
                    foreground="white",
                    font=("Arial", 8, "bold"),
                    relief='flat')
    style.map("Custom.Treeview",
              background=[('selected', '#0f3460')],
              foreground=[('selected', 'white')])

    tree = ttk.Treeview(frame, columns=columns, show=show,
                        height=height, style="Custom.Treeview")

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side=LEFT, fill=BOTH, expand=True)
    vsb.pack(side=RIGHT, fill=Y)

    # Aplicar colores alternados a las filas para mejorar la legibilidad
    tree.tag_configure('odd', background='#f8f9fa')
    tree.tag_configure('even', background='white')

    return frame, tree


def populate_tree(tree, rows, keys):
    """Llenar un Treeview con datos.

    tree: widget Treeview donde se insertan las filas.
    rows: lista de diccionarios con los datos.
    keys: lista de claves que se usan para obtener los valores.
    """
    tree.delete(*tree.get_children())
    for i, row in enumerate(rows):
        tag = 'odd' if i % 2 else 'even'
        values = [row.get(k, '') for k in keys]
        tree.insert('', END, values=values, tags=(tag,))


def make_search_bar(parent, var, command, placeholder="Buscar..."):
    """Crear una barra de búsqueda simple con icono y entrada.

    parent: contenedor donde se coloca la barra.
    var: variable StringVar que almacena el texto de búsqueda.
    command: función que se ejecuta cuando cambia el texto.
    placeholder: texto opcional de ayuda (no se usa directamente aquí).
    """
    frame = tk.Frame(parent, bg=CARD_BG)
    tk.Label(frame, text="🔍", bg=CARD_BG, font=("Arial", 11)).pack(side=LEFT, padx=(0,5))
    entry = tb.Entry(frame, textvariable=var, bootstyle="secondary", width=30, font=("Arial", 10))
    entry.pack(side=LEFT, ipady=4)
    entry.bind("<KeyRelease>", lambda e: command())
    return frame


def modal_dialog(parent, title, width=500, height=400):
    """Crear una ventana emergente modal centrada en la pantalla.

    Esta ventana bloquea la interacción con la ventana principal hasta cerrar.
    """
    top = tk.Toplevel(parent)
    top.title(title)
    top.resizable(False, False)
    top.grab_set()

    sw = top.winfo_screenwidth()
    sh = top.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - height) // 2
    top.geometry(f"{width}x{height}+{x}+{y}")
    top.configure(bg='white')
    return top


def form_field(parent, label, row, col=0, width=25, is_combo=False,
               values=None, textvariable=None, state='normal'):
    """Agregar un campo de formulario con etiqueta y entrada en un grid.

    label: texto de la etiqueta.
    row: fila del grid donde se coloca el campo.
    col: columna base para la etiqueta y el campo.
    is_combo: si True, crea un Combobox en lugar de un Entry.
    values: opciones para el Combobox.
    textvariable: variable asociada al campo.
    state: estado del campo ('normal' o 'readonly').
    """
    tk.Label(parent, text=label, font=("Arial", 9, "bold"),
             bg='white', fg='#555').grid(row=row, column=col*2,
             sticky='w', padx=(10,5), pady=5)
    if is_combo:
        w = tb.Combobox(parent, values=values or [], textvariable=textvariable,
                        width=width, state='readonly', font=("Arial", 9))
    else:
        w = tb.Entry(parent, textvariable=textvariable, width=width+2,
                     font=("Arial", 9), state=state)
    w.grid(row=row, column=col*2+1, sticky='ew', padx=(0,10), pady=5)
    return w


def stat_card(parent, label, value, color='#1a1a2e', icon=''):
    """Crear una tarjeta de estado con un título y un valor destacado.

    Se usa para mostrar métricas rápidas, totales o indicadores.
    """
    frame = tk.Frame(parent, bg=CARD_BG, padx=15, pady=12,
                     highlightbackground='#e0e0e0', highlightthickness=1)
    tk.Label(frame, text=f"{icon} {label}", font=("Arial", 8),
             bg=CARD_BG, fg='gray').pack(anchor='w')
    tk.Label(frame, text=value, font=("Arial", 15, "bold"),
             bg=CARD_BG, fg=color).pack(anchor='w')
    return frame
