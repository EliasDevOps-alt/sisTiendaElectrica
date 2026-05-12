import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from database.db import init_db
from controllers.controller import login


def _build_login(root):
    """Construye la pantalla de login dentro de root."""
    w, h = 400, 470
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
    root.title("Sistema de Ventas - Iniciar Sesión")
    root.resizable(False, False)

    frame_outer = tk.Frame(root, bg='#1a1a2e')
    frame_outer.pack(fill=BOTH, expand=True)

    card = tk.Frame(frame_outer, bg='white', padx=40, pady=35)
    card.place(relx=0.5, rely=0.5, anchor='center', width=320, height=365)

    tk.Label(card, text="🏪", font=("Arial", 38), bg='white').pack(pady=(8, 0))
    tk.Label(card, text="SISTEMA DE VENTAS", font=("Arial", 14, "bold"),
             bg='white', fg='#1a1a2e').pack()
    tk.Label(card, text="Ingrese sus credenciales", font=("Arial", 9),
             bg='white', fg='gray').pack(pady=(0, 18))

    tk.Label(card, text="Usuario", font=("Arial", 9, "bold"),
             bg='white', fg='#333', anchor='w').pack(fill=X)
    entry_user = tb.Entry(card, bootstyle="primary", font=("Arial", 11))
    entry_user.pack(fill=X, pady=(2, 12), ipady=6)

    tk.Label(card, text="Contraseña", font=("Arial", 9, "bold"),
             bg='white', fg='#333', anchor='w').pack(fill=X)
    entry_pass = tb.Entry(card, bootstyle="primary", font=("Arial", 11), show="●")
    entry_pass.pack(fill=X, pady=(2, 18), ipady=6)

    error_lbl = tk.Label(card, text="", font=("Arial", 9),
                         bg='white', fg='#e53935')
    error_lbl.pack()

    def do_login():
        user = entry_user.get().strip()
        pwd  = entry_pass.get().strip()
        if not user or not pwd:
            error_lbl.config(text="Complete usuario y contraseña")
            return
        usuario = login(user, pwd)
        if usuario:
            # Limpiar todo y cargar el sistema principal
            for widget in root.winfo_children():
                widget.destroy()
            root.resizable(True, True)
            root.title("Sistema de Ventas")
            root.state('zoomed')
            from views.main_window import MainWindow
            MainWindow.build_into(root, usuario)
        else:
            error_lbl.config(text="Usuario o contraseña incorrectos")
            entry_pass.delete(0, END)
            entry_pass.focus()

    tb.Button(card, text="INGRESAR", bootstyle="dark",
              command=do_login, width=20).pack(pady=(4, 8), ipady=4)

    tk.Label(card, text="admin / admin123  (por defecto)", font=("Arial", 7),
             bg='white', fg='lightgray').pack()

    entry_pass.bind("<Return>", lambda e: do_login())
    entry_user.insert(0, "admin")
    entry_pass.insert(0, "admin123")
    entry_user.focus()


def main():
    init_db()
    root = tb.Window(themename="cosmo")
    _build_login(root)
    root.mainloop()


if __name__ == "__main__":
    main()
