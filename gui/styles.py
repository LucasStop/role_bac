import os
from tkinter import ttk

def configure_app_style():
    style = ttk.Style()

    available_themes = style.theme_names()
    if 'clam' in available_themes:
        style.theme_use('clam')
    elif 'vista' in available_themes and os.name == 'nt':
        style.theme_use('vista')

    style.configure('TButton', font=('Arial', 10))
    style.configure('Treeview', font=('Arial', 9), rowheight=22)
    style.configure('Treeview.Heading', font=('Arial', 9, 'bold'))

    return style
