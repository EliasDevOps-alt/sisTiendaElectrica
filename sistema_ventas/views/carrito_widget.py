"""
CarritoWidget — tabla personalizada con soporte de texto multi-línea.
Columnas: # | Cód. | CANT.(UM) | DESCRIPCIÓN | MARCA | P.UNIT | DESC% | TOTAL
Doble clic en fila → callback para editar ítem.
"""
import tkinter as tk
from tkinter import font as tkfont

# Colores
BG_HDR   = '#1a1a2e'
FG_HDR   = '#ffffff'
BG_ODD   = '#ffffff'
BG_EVEN  = '#f8f9fa'
BG_SEL   = '#0f3460'
FG_SEL   = '#ffffff'
FG_NORM  = '#333333'
LINE_COL = '#e0e0e0'

# Definición de columnas: (clave, encabezado, ancho_px, anchor)
COLS = [
    ('num',            '#',         28,  'center'),
    ('codigo_proveedor','Cód.',      75,  'center'),
    ('cant_um',        'CANT.(UM)', 72,  'center'),
    ('descripcion_venta','DESCRIPCIÓN', 0, 'w'),   # ancho=0 → expansible
    ('marca_venta',    'MARCA',     70,  'center'),
    ('precio_unit',    'P.UNIT',    72,  'e'),
    ('pct_descuento',  'DESC%',     48,  'center'),
    ('total',          'TOTAL',     75,  'e'),
]

PAD_X  = 5
PAD_Y  = 4
HDR_H  = 24
FONT_N = ("Arial", 8)
FONT_B = ("Arial", 8, "bold")


class CarritoWidget(tk.Frame):
    def __init__(self, parent, on_doble_clic=None, **kwargs):
        super().__init__(parent, bg='white', **kwargs)
        self._on_doble_clic = on_doble_clic
        self._items  = []      # lista de dicts con datos del carrito
        self._sel    = None    # índice seleccionado

        self._fn     = tkfont.Font(family="Arial", size=8)
        self._fn_b   = tkfont.Font(family="Arial", size=8, weight="bold")

        # Canvas + scrollbar vertical
        self._vsb = tk.Scrollbar(self, orient='vertical')
        self._vsb.pack(side='right', fill='y')
        self._canvas = tk.Canvas(self, bg='white', highlightthickness=0,
                                 yscrollcommand=self._vsb.set)
        self._canvas.pack(side='left', fill='both', expand=True)
        self._vsb.config(command=self._canvas.yview)

        self._canvas.bind('<Configure>',    self._on_resize)
        self._canvas.bind('<Button-1>',     self._on_click)
        self._canvas.bind('<Double-Button-1>', self._on_dbl)
        self._canvas.bind('<MouseWheel>',   self._on_wheel)
        self._canvas.bind('<Button-4>',     self._on_wheel)
        self._canvas.bind('<Button-5>',     self._on_wheel)

    # ── API pública ─────────────────────────────────────────────
    def set_items(self, items):
        """items: lista de dicts igual que self.items_venta en ventas_view."""
        self._items = items
        self._sel   = None
        self._draw()

    def get_selected_index(self):
        return self._sel

    # ── Dibujo ──────────────────────────────────────────────────
    def _col_widths(self, total_w):
        """Calcula anchos reales; la col expansible (ancho=0) toma el resto."""
        fixed = sum(c[2] for c in COLS if c[2] > 0) + PAD_X * 2 * len(COLS)
        expand = max(total_w - fixed - self._vsb.winfo_width(), 60)
        return [expand if c[2] == 0 else c[2] for c in COLS]

    def _draw(self):
        c = self._canvas
        c.delete('all')
        total_w = c.winfo_width() or 600
        widths   = self._col_widths(total_w)

        # ── Encabezado ──
        x = 0
        for i, (col_info, w) in enumerate(zip(COLS, widths)):
            c.create_rectangle(x, 0, x+w+PAD_X*2, HDR_H,
                               fill=BG_HDR, outline='')
            c.create_text(x + PAD_X + w//2, HDR_H//2,
                          text=col_info[1], fill=FG_HDR,
                          font=self._fn_b, anchor='center')
            x += w + PAD_X * 2

        # ── Filas ──
        y = HDR_H
        self._row_y = []   # (y_top, y_bot) por fila

        for row_idx, item in enumerate(self._items):
            values = self._item_values(item, row_idx)
            bg = BG_SEL if row_idx == self._sel else (BG_ODD if row_idx%2==0 else BG_EVEN)
            fg = FG_SEL if row_idx == self._sel else FG_NORM

            # Calcular altura de fila según descripción
            desc_w   = widths[COLS.index(next(col for col in COLS if col[0]=='descripcion_venta'))]
            desc_txt = values[3]   # índice de descripcion_venta
            row_h    = self._text_height(desc_txt, desc_w) + PAD_Y * 2
            row_h    = max(row_h, 22)

            x = 0
            for col_idx, (col_info, w) in enumerate(zip(COLS, widths)):
                cell_x1, cell_y1 = x, y
                cell_x2, cell_y2 = x + w + PAD_X*2, y + row_h
                c.create_rectangle(cell_x1, cell_y1, cell_x2, cell_y2,
                                   fill=bg, outline=LINE_COL)
                txt     = values[col_idx]
                anchor  = col_info[3]
                txt_x   = (cell_x1 + PAD_X if anchor == 'w' else
                           cell_x2 - PAD_X if anchor == 'e' else
                           (cell_x1 + cell_x2)//2)
                # Descripción: wrapping manual
                if col_info[0] == 'descripcion_venta':
                    c.create_text(txt_x, cell_y1 + PAD_Y,
                                  text=txt, fill=fg, font=self._fn,
                                  anchor='nw', width=w)
                else:
                    c.create_text(txt_x, (cell_y1+cell_y2)//2,
                                  text=txt, fill=fg, font=self._fn,
                                  anchor=anchor if anchor in ('w','e') else 'center')
                x += w + PAD_X * 2

            self._row_y.append((y, y + row_h))
            y += row_h

        c.configure(scrollregion=(0, 0, total_w, y))

    def _text_height(self, text, wrap_width):
        """Estima altura de texto con wrapping."""
        if not text: return self._fn.metrics('linespace')
        ls  = self._fn.metrics('linespace')
        avg = self._fn.measure('n')
        chars_per_line = max(1, wrap_width // max(avg, 1))
        lines = 0
        for word_line in text.split('\n'):
            chars = len(word_line)
            lines += max(1, -(-chars // chars_per_line))   # ceil
        return lines * ls

    def _item_values(self, item, idx):
        cant = item['cantidad']
        um   = item.get('unidad_medida') or ''
        pu   = item.get('precio_venta_original', 0)
        tot  = cant * pu
        pct  = item.get('pct_descuento', 0)
        return [
            str(idx + 1),
            item.get('codigo_proveedor', ''),
            f"{cant} {um}".strip(),
            item.get('descripcion_venta') or item.get('descripcion', ''),
            item.get('marca_venta') or item.get('marca', ''),
            f"Bs.{pu:.2f}",
            f"{pct:.1f}%",
            f"Bs.{tot:.2f}",
        ]

    def _on_resize(self, event):
        self._draw()

    def _row_at(self, y_click):
        y_click += self._canvas.canvasy(0)
        for i, (y1, y2) in enumerate(getattr(self, '_row_y', [])):
            if y1 <= y_click < y2:
                return i
        return None

    def _on_click(self, event):
        idx = self._row_at(event.y)
        if idx is not None:
            self._sel = idx
            self._draw()

    def _on_dbl(self, event):
        idx = self._row_at(event.y)
        if idx is not None and self._on_doble_clic:
            self._sel = idx
            self._draw()
            self._on_doble_clic(idx)

    def _on_wheel(self, event):
        if event.num == 4:
            self._canvas.yview_scroll(-1, 'units')
        elif event.num == 5:
            self._canvas.yview_scroll(1, 'units')
        else:
            self._canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
