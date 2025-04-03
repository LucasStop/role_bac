import os
import tkinter as tk
from tkinter import font
from datetime import datetime
from gui.auth_screen import AuthScreen
from gui.styles import configure_app_style
from constants import CREDENTIALS_FILE, USER_DATA_FILE, FILES_DATA_DIR
from core.credentials import initialize_credentials
from gui.dashboard_screen import center_window 

def ensure_directories_exist():
    directories = [
        os.path.dirname(CREDENTIALS_FILE),
        os.path.dirname(USER_DATA_FILE),
        FILES_DATA_DIR
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"[{datetime.now()}] Diretório criado: {directory}")
            except Exception as e:
                print(f"[{datetime.now()}] Erro ao criar diretório {directory}: {str(e)}")

def main():
    try:
        print(f"[{datetime.now()}] Iniciando aplicação...")
        
        ensure_directories_exist()
        
        initialize_credentials()
        
        root = tk.Tk()
        root.title("Sistema de Controle de Acesso")
        root.minsize(400, 400)
        root.resizable(True, True)

        center_window(root, width=400, height=400)

        title_font = font.Font(family="Arial", size=14, weight="bold")
        normal_font = font.Font(family="Arial", size=10)
        button_font = font.Font(family="Arial", size=10, weight="bold")

        configure_app_style()
        
        app = AuthScreen(root, title_font, normal_font, button_font)
        root.mainloop()

    except Exception as e:
        print(f"[{datetime.now()}] Erro fatal na aplicação: {str(e)}")
        import traceback
        traceback.print_exc()
        from tkinter import messagebox
        messagebox.showerror("Erro Fatal", f"Ocorreu um erro inesperado:\n{str(e)}")
    finally:
        print(f"[{datetime.now()}] Aplicação finalizada.")

if __name__ == "__main__":
    main()
