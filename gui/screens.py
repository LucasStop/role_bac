# gui/screens.py
import tkinter as tk
from tkinter import messagebox, font, ttk, scrolledtext, simpledialog
from datetime import datetime, timedelta

from core.auth import authenticate_user, register_user
from core.credentials import load_credentials, initialize_credentials
from core.user_data import load_user_data
from core.file_manager import FileManager

from constants import AUTH_LOCKED, AUTH_NOT_FOUND, AUTH_SUCCESS, AUTH_WRONG_PASSWORD, LOCK_DURATION_MINUTES

class AuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Autenticação e Controle de Acesso")
        self.root.geometry("400x400")
        self.root.configure(bg="#f0f0f0")

        self.title_font = font.Font(family="Arial", size=14, weight="bold")
        self.normal_font = font.Font(family="Arial", size=10)
        self.button_font = font.Font(family="Arial", size=10, weight="bold")

        initialize_credentials()
        self.current_user = None
        self.file_manager = FileManager()
        self.current_file = None

        self.show_main_screen()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if self.current_user:
            response = messagebox.askquestion("Sair", "Você está conectado. Deseja realmente sair?")
            if response == 'yes':
                self.root.destroy()
        else:
            self.root.destroy()

    def show_main_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(main_frame, text="Sistema de Autenticação", font=self.title_font,
                 bg="#f0f0f0", fg="#333333").pack(pady=20)
        tk.Button(main_frame, text="Registrar Novo Usuário", font=self.button_font,
                 command=self.show_register_screen, bg="#4CAF50", fg="white",
                 width=25, height=2).pack(pady=10)
        tk.Button(main_frame, text="Fazer Login", font=self.button_font,
                 command=self.show_login_screen, bg="#2196F3", fg="white",
                 width=25, height=2).pack(pady=10)
        tk.Button(main_frame, text="Sair", font=self.button_font,
                 command=self.root.quit, bg="#f44336", fg="white",
                 width=25, height=2).pack(pady=10)

    def show_register_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        register_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        register_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(register_frame, text="Registrar Novo Usuário", font=self.title_font,
                 bg="#f0f0f0", fg="#333333").pack(pady=10)
        tk.Label(register_frame, text="Nome de Usuário:", font=self.normal_font,
                 bg="#f0f0f0").pack(anchor='w', pady=(10, 0))
        self.username_entry = tk.Entry(register_frame, font=self.normal_font, width=30)
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        tk.Label(register_frame, text="Senha:", font=self.normal_font,
                 bg="#f0f0f0").pack(anchor='w', pady=(10, 0))
        self.password_entry = tk.Entry(register_frame, font=self.normal_font, width=30, show="*")
        self.password_entry.pack(fill=tk.X, pady=(0, 10))
        tk.Label(register_frame, text="Defina as permissões iniciais:", font=self.normal_font,
                 bg="#f0f0f0").pack(anchor='w', pady=(10, 0))
        self.var_leitura = tk.BooleanVar(value=True)
        self.var_escrita = tk.BooleanVar(value=True)
        self.var_remocao = tk.BooleanVar(value=False)
        tk.Checkbutton(register_frame, text="Permissão de Leitura", variable=self.var_leitura, bg="#f0f0f0", font=self.normal_font).pack(anchor='w')
        tk.Checkbutton(register_frame, text="Permissão de Escrita", variable=self.var_escrita, bg="#f0f0f0", font=self.normal_font).pack(anchor='w')
        tk.Checkbutton(register_frame, text="Permissão de Remoção", variable=self.var_remocao, bg="#f0f0f0", font=self.normal_font).pack(anchor='w')
        button_frame = tk.Frame(register_frame, bg="#f0f0f0")
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Registrar", font=self.button_font, bg="#4CAF50", fg="white",
                  command=self.register_user_action).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Voltar", font=self.button_font, bg="#f44336", fg="white",
                  command=self.show_main_screen).pack(side=tk.LEFT, padx=10)

    def show_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        login_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        login_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(login_frame, text="Login de Usuário", font=self.title_font,
                 bg="#f0f0f0", fg="#333333").pack(pady=10)
        tk.Label(login_frame, text="Nome de Usuário:", font=self.normal_font,
                 bg="#f0f0f0").pack(anchor='w', pady=(10, 0))
        self.login_username_entry = tk.Entry(login_frame, font=self.normal_font, width=30)
        self.login_username_entry.pack(fill=tk.X, pady=(0, 10))
        tk.Label(login_frame, text="Senha:", font=self.normal_font,
                 bg="#f0f0f0").pack(anchor='w', pady=(10, 0))
        self.login_password_entry = tk.Entry(login_frame, font=self.normal_font, width=30, show="*")
        self.login_password_entry.pack(fill=tk.X, pady=(0, 10))
        button_frame = tk.Frame(login_frame, bg="#f0f0f0")
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Login", font=self.button_font, bg="#2196F3", fg="white",
                  command=self.login_user_action).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Voltar", font=self.button_font, bg="#f44336", fg="white",
                  command=self.show_main_screen).pack(side=tk.LEFT, padx=10)

    def register_user_action(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username:
            messagebox.showerror("Erro", "Nome de usuário não pode ser vazio")
            return
        if not password:
            messagebox.showerror("Erro", "Por favor, insira uma senha")
            return

        permissions = {
            "leitura": self.var_leitura.get(),
            "escrita": self.var_escrita.get(),
            "remocao": self.var_remocao.get()
        }

        success, message = register_user(username, password, permissions)
        if success:
            messagebox.showinfo("Sucesso", message)
            self.show_main_screen()
        else:
            messagebox.showerror("Erro", message)

    def login_user_action(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()

        if not username or not password:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos")
            return

        credentials = load_credentials()
        success, message = authenticate_user(username, password)

        if success:
            self.current_user = username
            messagebox.showinfo("Sucesso", f"Seja bem-vindo, {username}!")
            self.show_file_management_screen()
        else:
            if message == AUTH_LOCKED:
                user_data = load_user_data()
                lock_time_str = user_data[username]["security"]["lock_time"]
                lock_time = datetime.strptime(lock_time_str, "%Y-%m-%d %H:%M:%S")
                unlock_time = lock_time + timedelta(minutes=LOCK_DURATION_MINUTES)
                unlock_time_str = unlock_time.strftime("%H:%M:%S")
                messagebox.showerror("Conta Bloqueada", f"Esta conta foi bloqueada devido a várias tentativas falhas de login.\n\nA conta será desbloqueada automaticamente às {unlock_time_str}.\nEntre em contato com o administrador, se necessário.")
            elif message.startswith(AUTH_WRONG_PASSWORD):
                remaining = message.split(":")[1]
                messagebox.showerror("Erro", f"Senha incorreta. Tentativas restantes: {remaining}")
            elif message == AUTH_NOT_FOUND and username not in credentials:
                response = messagebox.askquestion("Usuário não encontrado", "Usuário não existe. Deseja criar uma conta?")
                if response == 'yes':
                    self.show_register_screen()
            else:
                messagebox.showerror("Erro", "Erro de autenticação desconhecido.")
