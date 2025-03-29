# gui/styles.py
import os
from tkinter import ttk

def configure_app_style():
    """
    Configura estilos personalizados para a aplicação usando ttk.Style

    O módulo ttk oferece temas e personalização de widgets.
    Referência: https://docs.python.org/3/library/tkinter.ttk.html#styles-and-themes
    """
    style = ttk.Style()

    available_themes = style.theme_names()
    if 'clam' in available_themes:
        style.theme_use('clam')
    elif 'vista' in available_themes and os.name == 'nt':  # Windows
        style.theme_use('vista')

    style.configure('TButton', font=('Arial', 10))
    style.configure('Treeview', font=('Arial', 9), rowheight=22)
    style.configure('Treeview.Heading', font=('Arial', 9, 'bold'))

    return style
