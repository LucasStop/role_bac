# gui/screens.py
import os
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

    def show_file_management_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title(f"Sistema de Arquivos - Usuário: {self.current_user}")
        
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        header_frame = tk.Frame(main_frame, bg="#e0e0e0", padx=10, pady=5)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text=f"Bem-vindo, {self.current_user}", 
                font=self.title_font, bg="#e0e0e0").pack(side=tk.LEFT)
                
        tk.Button(header_frame, text="Sair", command=self.logout, 
                 bg="#f44336", fg="white", font=self.button_font).pack(side=tk.RIGHT)
        
        operation_frame = tk.Frame(main_frame, bg="#f0f0f0", pady=10)
        operation_frame.pack(fill=tk.X)
        
        tk.Button(operation_frame, text="Novo Arquivo", command=self.create_new_file,
                 bg="#4CAF50", fg="white", font=self.button_font).pack(side=tk.LEFT, padx=5)
        
        tk.Button(operation_frame, text="Abrir", command=self.open_selected_file,
                 bg="#2196F3", fg="white", font=self.button_font).pack(side=tk.LEFT, padx=5)
                 
        tk.Button(operation_frame, text="Remover", command=self.remove_selected_file,
                 bg="#f44336", fg="white", font=self.button_font).pack(side=tk.LEFT, padx=5)
        
        file_list_frame = tk.Frame(main_frame, bg="#f0f0f0")
        file_list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(file_list_frame, text="Arquivos disponíveis:", 
                font=self.normal_font, bg="#f0f0f0").pack(anchor='w')
        
        self.file_tree = ttk.Treeview(file_list_frame, columns=("nome", "modificado"), 
                                    show="headings", selectmode="browse")
        self.file_tree.heading("nome", text="Nome do Arquivo")
        self.file_tree.heading("modificado", text="Última Modificação")
        self.file_tree.column("nome", width=250)
        self.file_tree.column("modificado", width=130)
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        self.file_tree.bind("<Double-1>", lambda event: self.open_selected_file())
        
        self.refresh_file_list()
        
        status_frame = tk.Frame(main_frame, bg="#e0e0e0", height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = tk.Label(status_frame, text="Pronto", bg="#e0e0e0", anchor='w')
        self.status_label.pack(fill=tk.X, padx=5)

    def refresh_file_list(self):
        for i in self.file_tree.get_children():
            self.file_tree.delete(i)
            
        files = self.file_manager.list_files()
        
        if not files:
            self.status_label.config(text="Nenhum arquivo encontrado")
            return
            
        for file in files:
            try:
                file_path = os.path.join(self.file_manager.folder, file)
                mod_time = os.path.getmtime(file_path)
                mod_time_str = datetime.fromtimestamp(mod_time).strftime('%d/%m/%Y %H:%M')
                
                self.file_tree.insert("", tk.END, values=(file, mod_time_str))
            except Exception as e:
                print(f"Erro ao processar arquivo {file}: {str(e)}")
                
        self.status_label.config(text=f"{len(files)} arquivo(s) encontrado(s)")

    def create_new_file(self):
        user_data = load_user_data()
        if not user_data[self.current_user]["permissions"]["escrita"]:
            messagebox.showerror("Sem permissão", "Você não tem permissão para criar arquivos.")
            return
            
        filename = simpledialog.askstring("Novo Arquivo", "Digite o nome do arquivo:")
        if not filename:
            return
            
        if "." not in filename:
            filename += ".txt"
            
        success, file_editor = self.open_file_editor(filename, "")
        if success:
            self.status_label.config(text=f"Editando novo arquivo: {filename}")
        else:
            messagebox.showerror("Erro", file_editor)

    def open_selected_file(self):
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showinfo("Selecione um arquivo", "Por favor, selecione um arquivo para abrir.")
            return
            
        filename = self.file_tree.item(selection[0], "values")[0]
        
        user_data = load_user_data()
        if not user_data[self.current_user]["permissions"]["leitura"]:
            messagebox.showerror("Sem permissão", "Você não tem permissão para ler arquivos.")
            return
            
        success, content = self.file_manager.read_file(filename)
        if success:
            self.open_file_editor(filename, content)
        else:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo: {content}")

    def open_file_editor(self, filename, content):
        editor_window = tk.Toplevel(self.root)
        editor_window.title(f"Editor - {filename}")
        editor_window.geometry("600x400")
        editor_window.minsize(400, 300)
        
        editor_frame = tk.Frame(editor_window)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_editor = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD, 
                                              font=('Courier', 10))
        text_editor.pack(fill=tk.BOTH, expand=True)
        text_editor.insert(tk.END, content)
        
        button_frame = tk.Frame(editor_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        user_data = load_user_data()
        can_write = user_data[self.current_user]["permissions"]["escrita"]
        
        save_button = tk.Button(
            button_frame, 
            text="Salvar", 
            command=lambda: self.save_file(filename, text_editor.get("1.0", tk.END), editor_window),
            state=tk.NORMAL if can_write else tk.DISABLED
        )
        save_button.pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Fechar", 
            command=editor_window.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        return True, editor_window

    def save_file(self, filename, content, editor_window=None):
        user_data = load_user_data()
        if not user_data[self.current_user]["permissions"]["escrita"]:
            messagebox.showerror("Sem permissão", "Você não tem permissão para salvar arquivos.")
            return
            
        if filename in self.file_manager.list_files():
            success, message = self.file_manager.edit_file(filename, content)
        else:
            success, message = self.file_manager.create_file(filename, content)
            
        if success:
            messagebox.showinfo("Sucesso", message)
            self.refresh_file_list()
            if editor_window:
                editor_window.title(f"Editor - {filename} (Salvo)")
        else:
            messagebox.showerror("Erro ao salvar", message)

    def remove_selected_file(self):
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showinfo("Selecione um arquivo", "Por favor, selecione um arquivo para remover.")
            return
            
        filename = self.file_tree.item(selection[0], "values")[0]
        
        user_data = load_user_data()
        if not user_data[self.current_user]["permissions"]["remocao"]:
            messagebox.showerror("Sem permissão", "Você não tem permissão para remover arquivos.")
            return
            
        confirm = messagebox.askyesno("Confirmar exclusão", 
                                    f"Tem certeza que deseja excluir o arquivo '{filename}'?")
        if not confirm:
            return
            
        success, message = self.file_manager.remove_file(filename)
        if success:
            messagebox.showinfo("Sucesso", message)
            self.refresh_file_list()
        else:
            messagebox.showerror("Erro ao remover", message)

    def logout(self):
        if messagebox.askyesno("Logout", "Deseja realmente sair da sua conta?"):
            self.current_user = None
            self.current_file = None
            self.show_main_screen()
