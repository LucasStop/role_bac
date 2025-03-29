# main.py
import os
import tkinter as tk
from datetime import datetime
from gui.screens import AuthApp
from gui.styles import configure_app_style
from constants import CREDENTIALS_FILE, USER_DATA_FILE

def ensure_directories_exist():
    """Garante que os diretórios necessários existam"""
    directories = [
        os.path.dirname(CREDENTIALS_FILE),
        os.path.dirname(USER_DATA_FILE),
        "data/arquivos"
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
        
        # Garantir que os diretórios necessários existam
        ensure_directories_exist()
        
        root = tk.Tk()
        root.title("Sistema de Controle de Acesso")
        root.minsize(400, 400)
        root.resizable(True, True)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width / 2 - 400 / 2)
        center_y = int(screen_height / 2 - 400 / 2)
        root.geometry(f'400x400+{center_x}+{center_y}')

        configure_app_style()
        app = AuthApp(root)
        root.mainloop()

    except Exception as e:
        print(f"[{datetime.now()}] Erro fatal na aplicação: {str(e)}")
        from tkinter import messagebox
        messagebox.showerror("Erro Fatal", f"Ocorreu um erro inesperado:\n{str(e)}")
    finally:
        print(f"[{datetime.now()}] Aplicação finalizada.")

if __name__ == "__main__":
    main()
