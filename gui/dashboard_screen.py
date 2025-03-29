import os
import tkinter as tk
from tkinter import font, ttk, messagebox, scrolledtext, simpledialog
from datetime import datetime

from core.file_manager import FileManager
from core.user_data import load_user_data

from gui.widgets import create_info_label, create_permission_label
from gui.file_editor import open_file_editor

class DashboardScreen:
    def __init__(self, root, title_font, normal_font, button_font, username, controller):
        self.root = root
        self.title_font = title_font
        self.normal_font = normal_font
        self.button_font = button_font
        self.username = username
        self.controller = controller
        self.file_manager = FileManager()

        # self.show_file_management_screen()

    def show_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title(f"Dashboard - {self.app.current_user}")
        self.root.geometry("800x600")

        main_container = tk.Frame(self.root, bg="#f5f5f5")
        main_container.pack(fill=tk.BOTH, expand=True)

        self._build_header(main_container)
        self._build_content(main_container)
        self._build_status_bar(main_container)
        self.refresh_file_list()

    def _build_header(self, parent):
        header = tk.Frame(parent, bg="#2c3e50", height=60)
        header.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))

        tk.Label(header, text="Sistema de Controle de Acesso",
                 font=font.Font(family="Arial", size=14, weight="bold"),
                 fg="white", bg="#2c3e50").pack(side=tk.LEFT, padx=20)

        user_frame = tk.Frame(header, bg="#2c3e50")
        user_frame.pack(side=tk.RIGHT, padx=20)

        tk.Label(user_frame, text=f"Usuário: {self.app.current_user}",
                 font=font.Font(family="Arial", size=10), fg="white", bg="#2c3e50").pack(side=tk.LEFT, padx=10)
        tk.Button(user_frame, text="Sair", command=self.app.logout,
                  bg="#e74c3c", fg="white", font=font.Font(family="Arial", size=9)).pack(side=tk.LEFT)

    def _build_content(self, parent):
        container = tk.Frame(parent, bg="#f5f5f5")
        container.pack(fill=tk.BOTH, expand=True)

        self._build_sidebar(container)
        self._build_main_panel(container)

    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg="#34495e", width=200)
        sidebar.pack(fill=tk.Y, side=tk.LEFT, padx=(0, 10))
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Informações",
                 font=font.Font(family="Arial", size=12, weight="bold"),
                 fg="white", bg="#34495e").pack(pady=(20, 10), padx=10, anchor='w')

        user_info = load_user_data().get(self.app.current_user, {})

        info_frame = tk.Frame(sidebar, bg="#34495e", padx=10, pady=5)
        info_frame.pack(fill=tk.X)

        create_info_label(info_frame, "Último login:", user_info.get("last_login", "Primeiro acesso"))
        create_info_label(info_frame, "Total de logins:", str(user_info.get("login_count", "1")))
        create_info_label(info_frame, "Conta criada em:", user_info.get("created_at", "Desconhecido"))

        ttk.Separator(sidebar, orient='horizontal').pack(fill=tk.X, pady=10)

        tk.Label(sidebar, text="Permissões",
                 font=font.Font(family="Arial", size=12, weight="bold"),
                 fg="white", bg="#34495e").pack(pady=(10, 5), padx=10, anchor='w')

        permissions = user_info.get("permissions", {})
        create_permission_label(sidebar, "Leitura", permissions.get("leitura", False))
        create_permission_label(sidebar, "Escrita", permissions.get("escrita", False))
        create_permission_label(sidebar, "Remoção", permissions.get("remocao", False))

    def _build_main_panel(self, parent):
        main_panel = tk.Frame(parent, bg="white")
        main_panel.pack(fill=tk.BOTH, expand=True)

        actions_frame = tk.Frame(main_panel, bg="#ecf0f1", height=40, padx=10, pady=10)
        actions_frame.pack(fill=tk.X)

        tk.Label(actions_frame, text="ARQUIVOS DO SISTEMA",
                 font=font.Font(family="Arial", size=12, weight="bold"),
                 bg="#ecf0f1").pack(side=tk.LEFT)

        user_data = load_user_data()
        permissions = user_data[self.app.current_user].get("permissions", {})

        tk.Button(actions_frame, text="Novo Arquivo", command=self.create_new_file,
                  bg="#2ecc71", fg="white", padx=10,
                  state=tk.NORMAL if permissions.get("escrita") else tk.DISABLED).pack(side=tk.RIGHT, padx=5)

        tk.Button(actions_frame, text="Atualizar Lista", command=self.refresh_file_list,
                  bg="#3498db", fg="white", padx=10).pack(side=tk.RIGHT, padx=5)

        files_container = tk.Frame(main_panel, bg="white", padx=10, pady=10)
        files_container.pack(fill=tk.BOTH, expand=True)

        columns = ("nome", "tamanho", "modificado", "permissoes")
        self.file_tree = ttk.Treeview(files_container, columns=columns, show="headings", selectmode="browse")

        self.file_tree.heading("nome", text="Nome do Arquivo")
        self.file_tree.heading("tamanho", text="Tamanho")
        self.file_tree.heading("modificado", text="Última Modificação")
        self.file_tree.heading("permissoes", text="Ações")

        self.file_tree.column("nome", width=250, anchor='w')
        self.file_tree.column("tamanho", width=100, anchor='center')
        self.file_tree.column("modificado", width=150, anchor='center')
        self.file_tree.column("permissoes", width=150, anchor='center')

        scrollbar = ttk.Scrollbar(files_container, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_tree.bind("<Double-1>", lambda e: self.open_selected_file())

    def _build_status_bar(self, parent):
        status = tk.Frame(parent, bg="#7f8c8d", height=25)
        status.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = tk.Label(status, text="Pronto", fg="white", bg="#7f8c8d", anchor='w')
        self.status_label.pack(fill=tk.X, padx=10, pady=3)

    def refresh_file_list(self):
        for i in self.file_tree.get_children():
            self.file_tree.delete(i)

        files = self.file_manager.list_files()
        file_count = len(files)
        user_data = load_user_data()
        permissions = user_data[self.app.current_user].get("permissions", {})
        can_read = permissions.get("leitura")
        can_write = permissions.get("escrita")
        can_delete = permissions.get("remocao")

        for file in files:
            try:
                path = os.path.join(self.file_manager.folder, file)
                size = self._format_size(os.path.getsize(path))
                mod_time = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%d/%m/%Y %H:%M')
                actions = []
                if can_read: actions.append("Ler")
                if can_write: actions.append("Editar")
                if can_delete: actions.append("Remover")
                actions_str = ", ".join(actions) if actions else "Sem permissões"
                self.file_tree.insert("", tk.END, values=(file, size, mod_time, actions_str))
            except Exception as e:
                print(f"Erro ao processar arquivo {file}: {e}")

        self.status_label.config(text=f"{file_count} arquivo(s) encontrado(s) no sistema")

    def _format_size(self, size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size/1024:.1f} KB"
        elif size < 1024 ** 3:
            return f"{size/(1024**2):.1f} MB"
        else:
            return f"{size/(1024**3):.1f} GB"

    def create_new_file(self):
        user_data = load_user_data()
        if not user_data[self.app.current_user]["permissions"].get("escrita"):
            messagebox.showerror("Sem permissão", "Você não tem permissão para criar arquivos.")
            return

        filename = simpledialog.askstring("Novo Arquivo", "Digite o nome do arquivo:")
        if not filename:
            return

        if "." not in filename:
            filename += ".txt"

        success, editor = open_file_editor(self.root, self.file_manager, self.app.current_user, filename, "")
        if success:
            self.status_label.config(text=f"Editando novo arquivo: {filename}")

    def open_selected_file(self):
        selection = self.file_tree.selection()
        if not selection:
            return

        filename = self.file_tree.item(selection[0], "values")[0]
        user_data = load_user_data()

        if not user_data[self.app.current_user]["permissions"].get("leitura"):
            messagebox.showerror("Sem permissão", "Você não tem permissão para ler arquivos.")
            return

        success, content = self.file_manager.read_file(filename)
        if success:
            open_file_editor(self.root, self.file_manager, self.app.current_user, filename, content)
            self.status_label.config(text=f"Arquivo aberto: {filename}")
        else:
            messagebox.showerror("Erro", f"Erro ao abrir arquivo: {content}")