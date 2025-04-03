CREDENTIALS_FILE = "data/credentials.json"
USER_DATA_FILE = "data/user_data.json"
FILES_DATA_DIR = "data/arquivos/"

MAX_LOGIN_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 15

AUTH_SUCCESS = "success"
AUTH_LOCKED = "locked"
AUTH_NOT_FOUND = "not_found"
AUTH_WRONG_PASSWORD = "wrong_password"

import os
import json
import time
import secrets
import hashlib
import tkinter as tk
from tkinter import ttk, font, messagebox, scrolledtext, simpledialog
from datetime import datetime, timedelta


def ensure_directories_exist():
    directories = [
        os.path.dirname(CREDENTIALS_FILE),
        os.path.dirname(USER_DATA_FILE),
        FILES_DATA_DIR,
    ]

    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"[{datetime.now()}] Diretório criado: {directory}")
            except Exception as e:
                print(
                    f"[{datetime.now()}] Erro ao criar diretório {directory}: {str(e)}"
                )


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


def generate_salt():
    return secrets.token_hex(16)


def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()


def verify_password(stored_hash, stored_salt, provided_password):
    return hash_password(provided_password, stored_salt) == stored_hash


def create_info_label(parent, label_text, value_text):
    frame = tk.Frame(parent, bg="#34495e")
    frame.pack(fill=tk.X, pady=2)

    tk.Label(
        frame,
        text=label_text,
        font=font.Font(family="Arial", size=9),
        fg="#bdc3c7",
        bg="#34495e",
        width=12,
        anchor="w",
    ).pack(side=tk.LEFT)

    tk.Label(
        frame,
        text=value_text,
        font=font.Font(family="Arial", size=9),
        fg="white",
        bg="#34495e",
        anchor="w",
    ).pack(side=tk.LEFT, padx=5)


def create_permission_label(parent, permission_name, has_permission):
    frame = tk.Frame(parent, bg="#34495e", padx=10, pady=2)
    frame.pack(fill=tk.X)

    status_color = "#2ecc71" if has_permission else "#e74c3c"
    status_text = "✓" if has_permission else "✗"

    tk.Label(
        frame,
        text=permission_name + ":",
        font=font.Font(family="Arial", size=9),
        fg="#bdc3c7",
        bg="#34495e",
        anchor="w",
    ).pack(side=tk.LEFT)

    tk.Label(
        frame,
        text=status_text,
        font=font.Font(family="Arial", size=9, weight="bold"),
        fg=status_color,
        bg="#34495e",
        width=2,
    ).pack(side=tk.RIGHT)


def configure_app_style():
    style = ttk.Style()

    available_themes = style.theme_names()
    if "clam" in available_themes:
        style.theme_use("clam")
    elif "vista" in available_themes and os.name == "nt":
        style.theme_use("vista")

    style.configure("TButton", font=("Arial", 10))
    style.configure("Treeview", font=("Arial", 9), rowheight=22)
    style.configure("Treeview.Heading", font=("Arial", 9, "bold"))

    return style


class AuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Autenticação e Controle de Acesso")
        self.root.geometry("400x400")
        self.root.configure(bg="#f0f0f0")

        initialize_credentials()
        self.current_user = None

        self.auth_screen = AuthScreen(self)
        self.dashboard_screen = DashboardScreen(self)

        self.show_main_screen()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if self.current_user:
            response = messagebox.askquestion(
                "Sair", "Você está conectado. Deseja realmente sair?"
            )
            if response == "yes":
                self.root.destroy()
        else:
            self.root.destroy()

    def show_main_screen(self):
        self.auth_screen.show_main_menu()

    def show_register_screen(self):
        self.auth_screen.show_register_screen()

    def show_login_screen(self):
        self.auth_screen.show_login_screen()

    def show_dashboard(self, username):
        self.current_user = username
        self.dashboard_screen.show_dashboard()

    def logout(self):
        if messagebox.askyesno("Logout", "Deseja realmente sair da sua conta?"):
            self.current_user = None
            self.show_main_screen()


def center_window(window, width=None, height=None):
    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()

    window.update_idletasks()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)

    window.geometry(f"{width}x{height}+{x}+{y}")


class DashboardScreen:
    def __init__(
        self, root, title_font, normal_font, button_font, username, controller
    ):
        self.root = root
        self.title_font = title_font
        self.normal_font = normal_font
        self.button_font = button_font
        self.username = username
        self.controller = controller
        self.file_manager = FileManager()
        self.status_label = None

    def show_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title(f"Dashboard - {self.username}")

        center_window(self.root, width=1000, height=600)

        main_container = tk.Frame(self.root, bg="#f5f5f5")
        main_container.pack(fill=tk.BOTH, expand=True)

        self._build_header(main_container)
        self._build_content(main_container)
        self._build_status_bar(main_container)
        self.refresh_file_list()

    def _build_header(self, parent):
        header = tk.Frame(parent, bg="#2c3e50", height=60)
        header.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))

        tk.Label(
            header,
            text="Sistema de Controle de Acesso",
            font=font.Font(family="Arial", size=14, weight="bold"),
            fg="white",
            bg="#2c3e50",
        ).pack(side=tk.LEFT, padx=20)

        user_frame = tk.Frame(header, bg="#2c3e50")
        user_frame.pack(side=tk.RIGHT, padx=20)

        tk.Label(
            user_frame,
            text=f"Usuário: {self.username}",
            font=font.Font(family="Arial", size=10),
            fg="white",
            bg="#2c3e50",
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            user_frame,
            text="Sair",
            command=self.controller.logout,
            bg="#e74c3c",
            fg="white",
            font=font.Font(family="Arial", size=9),
        ).pack(side=tk.LEFT)

    def _build_content(self, parent):
        container = tk.Frame(parent, bg="#f5f5f5")
        container.pack(fill=tk.BOTH, expand=True)

        self._build_sidebar(container)
        self._build_main_panel(container)

    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg="#34495e", width=200)
        sidebar.pack(fill=tk.Y, side=tk.LEFT, padx=(0, 10))
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="Informações",
            font=font.Font(family="Arial", size=12, weight="bold"),
            fg="white",
            bg="#34495e",
        ).pack(pady=(20, 10), padx=10, anchor="w")

        user_info = load_user_data().get(self.username, {})

        info_frame = tk.Frame(sidebar, bg="#34495e", padx=10, pady=5)
        info_frame.pack(fill=tk.X)

        self.create_info_label(
            info_frame, "Último login:", user_info.get("last_login", "Primeiro acesso")
        )
        self.create_info_label(
            info_frame, "Total de logins:", str(user_info.get("login_count", "1"))
        )
        self.create_info_label(
            info_frame, "Conta criada em:", user_info.get("created_at", "Desconhecido")
        )

        ttk.Separator(sidebar, orient="horizontal").pack(fill=tk.X, pady=10)

        tk.Label(
            sidebar,
            text="Permissões",
            font=font.Font(family="Arial", size=12, weight="bold"),
            fg="white",
            bg="#34495e",
        ).pack(pady=(10, 5), padx=10, anchor="w")

        permissions = user_info.get("permissions", {})
        self.create_permission_label(
            sidebar, "Leitura", permissions.get("leitura", False)
        )
        self.create_permission_label(
            sidebar, "Escrita", permissions.get("escrita", False)
        )
        self.create_permission_label(
            sidebar, "Remoção", permissions.get("remocao", False)
        )

    def _build_main_panel(self, parent):
        main_panel = tk.Frame(parent, bg="white")
        main_panel.pack(fill=tk.BOTH, expand=True)

        actions_frame = tk.Frame(main_panel, bg="#ecf0f1", height=40, padx=10, pady=10)
        actions_frame.pack(fill=tk.X)

        tk.Label(
            actions_frame,
            text="ARQUIVOS DO SISTEMA",
            font=font.Font(family="Arial", size=12, weight="bold"),
            bg="#ecf0f1",
        ).pack(side=tk.LEFT)

        user_data = load_user_data()
        permissions = user_data[self.username].get("permissions", {})

        if permissions.get("escrita"):
            create_button = tk.Menubutton(
                actions_frame,
                text="Novo Arquivo",
                bg="#2ecc71",
                fg="white",
                relief=tk.RAISED,
            )
            create_button.pack(side=tk.RIGHT, padx=5)

            create_menu = tk.Menu(create_button, tearoff=0)
            create_button.configure(menu=create_menu)

            create_menu.add_command(
                label="Texto (.txt)", command=lambda: self.create_new_file(".txt")
            )
            create_menu.add_command(
                label="Desenho (.draw)", command=lambda: self.create_new_file(".draw")
            )
            create_menu.add_command(
                label="Planilha (.sheet)",
                command=lambda: self.create_new_file(".sheet"),
            )
        else:
            tk.Button(
                actions_frame,
                text="Novo Arquivo",
                state=tk.DISABLED,
                bg="#2ecc71",
                fg="white",
                padx=10,
            ).pack(side=tk.RIGHT, padx=5)

        if permissions.get("remocao"):
            tk.Button(
                actions_frame,
                text="Excluir Arquivo",
                command=self.remove_selected_file,
                bg="#e74c3c",
                fg="white",
                padx=10,
            ).pack(side=tk.RIGHT, padx=5)

        tk.Button(
            actions_frame,
            text="Atualizar Lista",
            command=self.refresh_file_list,
            bg="#3498db",
            fg="white",
            padx=10,
        ).pack(side=tk.RIGHT, padx=5)

        files_container = tk.Frame(main_panel, bg="white", padx=10, pady=10)
        files_container.pack(fill=tk.BOTH, expand=True)

        columns = ("nome", "tipo", "tamanho", "modificado", "permissoes")
        self.file_tree = ttk.Treeview(
            files_container, columns=columns, show="headings", selectmode="browse"
        )

        self.file_tree.heading("nome", text="Nome do Arquivo")
        self.file_tree.heading("tipo", text="Tipo")
        self.file_tree.heading("tamanho", text="Tamanho")
        self.file_tree.heading("modificado", text="Última Modificação")
        self.file_tree.heading("permissoes", text="Ações")

        self.file_tree.column("nome", width=200, anchor="w")
        self.file_tree.column("tipo", width=80, anchor="center")
        self.file_tree.column("tamanho", width=80, anchor="center")
        self.file_tree.column("modificado", width=150, anchor="center")
        self.file_tree.column("permissoes", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(
            files_container, orient="vertical", command=self.file_tree.yview
        )
        self.file_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_tree.bind("<Double-1>", lambda e: self.open_selected_file())

    def _build_status_bar(self, parent):
        status = tk.Frame(parent, bg="#7f8c8d", height=25)
        status.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = tk.Label(
            status, text="Pronto", fg="white", bg="#7f8c8d", anchor="w"
        )
        self.status_label.pack(fill=tk.X, padx=10, pady=3)

    def create_info_label(self, parent, label_text, value_text):
        frame = tk.Frame(parent, bg="#34495e")
        frame.pack(fill=tk.X, pady=2)

        tk.Label(
            frame,
            text=label_text,
            font=font.Font(family="Arial", size=9),
            fg="#bdc3c7",
            bg="#34495e",
            width=12,
            anchor="w",
        ).pack(side=tk.LEFT)

        tk.Label(
            frame,
            text=value_text,
            font=font.Font(family="Arial", size=9),
            fg="white",
            bg="#34495e",
            anchor="w",
        ).pack(side=tk.LEFT, padx=5)

    def create_permission_label(self, parent, permission_name, has_permission):
        frame = tk.Frame(parent, bg="#34495e", padx=10, pady=2)
        frame.pack(fill=tk.X)

        status_color = "#2ecc71" if has_permission else "#e74c3c"
        status_text = "✓" if has_permission else "✗"

        tk.Label(
            frame,
            text=permission_name + ":",
            font=font.Font(family="Arial", size=9),
            fg="#bdc3c7",
            bg="#34495e",
            anchor="w",
        ).pack(side=tk.LEFT)

        tk.Label(
            frame,
            text=status_text,
            font=font.Font(family="Arial", size=9, weight="bold"),
            fg=status_color,
            bg="#34495e",
            width=2,
        ).pack(side=tk.RIGHT)

    def refresh_file_list(self):
        try:
            if not hasattr(self, "file_tree") or not self.file_tree.winfo_exists():
                return

            for i in self.file_tree.get_children():
                self.file_tree.delete(i)

            files = self.file_manager.list_files()
            file_count = len(files) if files else 0

            user_data = load_user_data()
            permissions = user_data[self.username].get("permissions", {})
            can_read = permissions.get("leitura")
            can_write = permissions.get("escrita")
            can_delete = permissions.get("remocao")

            for file in files:
                try:
                    path = os.path.join(self.file_manager.folder, file)
                    size = self._format_size(os.path.getsize(path))
                    mod_time = datetime.fromtimestamp(os.path.getmtime(path)).strftime(
                        "%d/%m/%Y %H:%M"
                    )

                    if file.endswith(".txt"):
                        file_type = "Texto"
                    elif file.endswith(".draw"):
                        file_type = "Desenho"
                    elif file.endswith(".sheet"):
                        file_type = "Planilha"
                    else:
                        file_type = "Desconhecido"

                    actions = []
                    if can_read:
                        actions.append("Ler")
                    if can_write:
                        actions.append("Editar")
                    if can_delete:
                        actions.append("Remover")
                    actions_str = ", ".join(actions) if actions else "Sem permissões"

                    self.file_tree.insert(
                        "",
                        tk.END,
                        values=(file, file_type, size, mod_time, actions_str),
                    )
                except Exception as e:
                    print(f"Erro ao processar arquivo {file}: {e}")

            if self.status_label and self.status_label.winfo_exists():
                self.status_label.config(
                    text=f"{file_count} arquivo(s) encontrado(s) no sistema"
                )
        except tk.TclError as e:
            print(f"[Aviso] Erro ao atualizar lista de arquivos: {e}")
        except Exception as e:
            print(f"[Erro] Exceção ao atualizar lista de arquivos: {e}")

    def safe_refresh_file_list(self):
        try:
            self.refresh_file_list()
        except tk.TclError as e:
            print(f"[Aviso] Impossível atualizar lista: widget destruído. {e}")
        except Exception as e:
            print(f"[Erro] Exceção ao atualizar lista de arquivos: {e}")

    def _format_size(self, size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024**2:
            return f"{size/1024:.1f} KB"
        elif size < 1024**3:
            return f"{size/(1024**2):.1f} MB"
        else:
            return f"{size/(1024**3):.1f} GB"

    def create_new_file(self, default_extension=".txt"):
        user_data = load_user_data()
        if not user_data[self.username]["permissions"].get("escrita"):
            messagebox.showerror(
                "Sem permissão", "Você não tem permissão para criar arquivos."
            )
            return

        filename = simpledialog.askstring("Novo Arquivo", "Digite o nome do arquivo:")
        if not filename:
            return

        if "." not in filename:
            filename += default_extension

        if default_extension == ".draw" and not filename.endswith(".draw"):
            filename += ".draw"
        elif default_extension == ".sheet" and not filename.endswith(".sheet"):
            filename += ".sheet"
        elif default_extension == ".txt" and not (
            filename.endswith(".txt")
            or filename.endswith(".draw")
            or filename.endswith(".sheet")
        ):
            filename += ".txt"

        if filename in self.file_manager.list_files():
            result, msg = self.file_manager.read_file(filename)
            if result:
                content = msg
            else:
                content = ""
        else:
            if filename.endswith(".draw"):
                content = '{"strokes": [], "current_stroke": []}'
            elif filename.endswith(".sheet"):
                content = '{"rows": 10, "columns": 5, "cells": {}}'
            else:
                content = ""

            result, msg = self.file_manager.create_file(filename, content)
            if not result:
                messagebox.showerror("Erro", f"Não foi possível criar o arquivo: {msg}")
                return

        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        center_window(self.root, width=1000, height=600)

        if filename.endswith(".draw"):
            open_draw_editor(
                self.root,
                main_frame,
                self.file_manager,
                self.username,
                filename,
                content,
                self.show_dashboard,
                self.safe_refresh_file_list,
            )
        elif filename.endswith(".sheet"):
            open_sheet_editor(
                self.root,
                main_frame,
                self.file_manager,
                self.username,
                filename,
                content,
                self.show_dashboard,
                self.safe_refresh_file_list,
            )
        else:
            open_file_editor(
                self.root,
                main_frame,
                self.file_manager,
                self.username,
                filename,
                content,
                self.show_dashboard,
                self.safe_refresh_file_list,
            )

    def open_selected_file(self):
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showinfo(
                "Selecione um arquivo", "Por favor, selecione um arquivo para abrir."
            )
            return

        filename = self.file_tree.item(selection[0], "values")[0]
        user_data = load_user_data()

        if not user_data[self.username]["permissions"].get("leitura"):
            messagebox.showerror(
                "Sem permissão", "Você não tem permissão para ler arquivos."
            )
            return

        success, content = self.file_manager.read_file(filename)
        if success:
            for widget in self.root.winfo_children():
                widget.destroy()

            main_frame = tk.Frame(self.root)
            main_frame.pack(fill=tk.BOTH, expand=True)

            center_window(self.root, width=1000, height=600)

            if filename.endswith(".draw"):
                open_draw_editor(
                    self.root,
                    main_frame,
                    self.file_manager,
                    self.username,
                    filename,
                    content,
                    self.show_dashboard,
                    self.safe_refresh_file_list,
                )
            elif filename.endswith(".sheet"):
                open_sheet_editor(
                    self.root,
                    main_frame,
                    self.file_manager,
                    self.username,
                    filename,
                    content,
                    self.show_dashboard,
                    self.safe_refresh_file_list,
                )
            else:
                open_file_editor(
                    self.root,
                    main_frame,
                    self.file_manager,
                    self.username,
                    filename,
                    content,
                    self.show_dashboard,
                    self.safe_refresh_file_list,
                )
        else:
            messagebox.showerror("Erro", f"Erro ao abrir arquivo: {content}")

    def remove_selected_file(self):
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showinfo(
                "Selecione um arquivo", "Por favor, selecione um arquivo para remover."
            )
            return

        filename = self.file_tree.item(selection[0], "values")[0]

        user_data = load_user_data()
        if not user_data[self.username]["permissions"].get("remocao"):
            messagebox.showerror(
                "Sem permissão", "Você não tem permissão para remover arquivos."
            )
            return

        confirm = messagebox.askyesno(
            "Confirmar exclusão",
            f"Tem certeza que deseja excluir o arquivo '{filename}'?",
        )
        if not confirm:
            return

        success, message = self.file_manager.remove_file(filename)
        if success:
            messagebox.showinfo("Sucesso", message)
            self.safe_refresh_file_list()
        else:
            messagebox.showerror("Erro ao remover", message)


class AuthScreen:
    def __init__(self, root, title_font, normal_font, button_font):
        self.root = root
        self.title_font = title_font
        self.normal_font = normal_font
        self.button_font = button_font
        self.current_user = None

        self.dashboard = None

        self.show_main_menu()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear_screen()
        center_window(self.root, width=400, height=400)
        self.root.title("Sistema de Autenticação")

        frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="Sistema de Autenticação",
            font=self.title_font,
            bg="#f0f0f0",
            fg="#333333",
        ).pack(pady=15)

        tk.Button(
            frame,
            text="Registrar Novo Usuário",
            font=self.button_font,
            command=self.show_register_screen,
            bg="#4CAF50",
            fg="white",
            width=25,
            height=2,
        ).pack(pady=8)

        tk.Button(
            frame,
            text="Fazer Login",
            font=self.button_font,
            command=self.show_login_screen,
            bg="#2196F3",
            fg="white",
            width=25,
            height=2,
        ).pack(pady=8)

        tk.Button(
            frame,
            text="Sair",
            font=self.button_font,
            command=self.root.quit,
            bg="#f44336",
            fg="white",
            width=25,
            height=2,
        ).pack(pady=8)

    def show_register_screen(self):
        self.clear_screen()
        center_window(self.root, width=400, height=500)
        self.root.title("Registro de Usuário")

        frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="Registrar Novo Usuário",
            font=self.title_font,
            bg="#f0f0f0",
            fg="#333333",
        ).pack(pady=10)

        tk.Label(
            frame, text="Nome de Usuário:", font=self.normal_font, bg="#f0f0f0"
        ).pack(anchor="w", pady=10)
        self.username_entry = tk.Entry(frame, font=self.normal_font, width=30)
        self.username_entry.pack(fill=tk.X, pady=10)

        tk.Label(frame, text="Senha:", font=self.normal_font, bg="#f0f0f0").pack(
            anchor="w", pady=10
        )
        self.password_entry = tk.Entry(frame, font=self.normal_font, width=30, show="*")
        self.password_entry.pack(fill=tk.X, pady=10)

        tk.Label(
            frame,
            text="Defina as permissões iniciais:",
            font=self.normal_font,
            bg="#f0f0f0",
        ).pack(anchor="w", pady=10)
        self.var_leitura = tk.BooleanVar(value=True)
        self.var_escrita = tk.BooleanVar(value=True)
        self.var_remocao = tk.BooleanVar(value=False)
        tk.Checkbutton(
            frame,
            text="Permissão de Leitura",
            variable=self.var_leitura,
            bg="#f0f0f0",
            font=self.normal_font,
        ).pack(anchor="w")
        tk.Checkbutton(
            frame,
            text="Permissão de Escrita",
            variable=self.var_escrita,
            bg="#f0f0f0",
            font=self.normal_font,
        ).pack(anchor="w")
        tk.Checkbutton(
            frame,
            text="Permissão de Remoção",
            variable=self.var_remocao,
            bg="#f0f0f0",
            font=self.normal_font,
        ).pack(anchor="w")

        button_frame = tk.Frame(frame, bg="#f0f0f0")
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="Registrar",
            font=self.button_font,
            bg="#4CAF50",
            fg="white",
            command=self.register_user_action,
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            button_frame,
            text="Voltar",
            font=self.button_font,
            bg="#f44336",
            fg="white",
            command=self.show_main_menu,
        ).pack(side=tk.LEFT, padx=10)

    def show_login_screen(self):
        self.clear_screen()
        center_window(self.root, width=400, height=400)
        self.root.title("Login de Usuário")

        frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="Login de Usuário",
            font=self.title_font,
            bg="#f0f0f0",
            fg="#333333",
        ).pack(pady=10)

        tk.Label(
            frame, text="Nome de Usuário:", font=self.normal_font, bg="#f0f0f0"
        ).pack(anchor="w", pady=10)
        self.login_username_entry = tk.Entry(frame, font=self.normal_font, width=30)
        self.login_username_entry.pack(fill=tk.X, pady=10)

        tk.Label(frame, text="Senha:", font=self.normal_font, bg="#f0f0f0").pack(
            anchor="w", pady=10
        )
        self.login_password_entry = tk.Entry(
            frame, font=self.normal_font, width=30, show="*"
        )
        self.login_password_entry.pack(fill=tk.X, pady=10)

        button_frame = tk.Frame(frame, bg="#f0f0f0")
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="Login",
            font=self.button_font,
            bg="#2196F3",
            fg="white",
            command=self.login_user_action,
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            button_frame,
            text="Voltar",
            font=self.button_font,
            bg="#f44336",
            fg="white",
            command=self.show_main_menu,
        ).pack(side=tk.LEFT, padx=10)

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
            "remocao": self.var_remocao.get(),
        }

        success, message = register_user(username, password, permissions)
        if success:
            messagebox.showinfo("Sucesso", message)
            self.show_main_menu()
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
            self.show_dashboard(username)
        else:
            if message == AUTH_LOCKED:
                user_data = load_user_data()
                lock_time_str = user_data[username]["security"]["lock_time"]
                lock_time = datetime.strptime(lock_time_str, "%Y-%m-%d %H:%M:%S")
                unlock_time = lock_time + timedelta(minutes=LOCK_DURATION_MINUTES)
                unlock_time_str = unlock_time.strftime("%H:%M:%S")
                messagebox.showerror(
                    "Conta Bloqueada",
                    f"Esta conta foi bloqueada devido a várias tentativas falhas de login.\n\nA conta será desbloqueada automaticamente às {unlock_time_str}.\nEntre em contato com o administrador, se necessário.",
                )
            elif message.startswith(AUTH_WRONG_PASSWORD):
                remaining = message.split(":")[1]
                messagebox.showerror(
                    "Erro", f"Senha incorreta. Tentativas restantes: {remaining}"
                )
            elif message == AUTH_NOT_FOUND and username not in credentials:
                response = messagebox.askquestion(
                    "Usuário não encontrado",
                    "Usuário não existe. Deseja criar uma conta?",
                )
                if response == "yes":
                    self.show_register_screen()
            else:
                messagebox.showerror("Erro", "Erro de autenticação desconhecido.")

    def show_dashboard(self, username):
        self.current_user = username
        self.root.title(f"Dashboard - {username}")

        if self.dashboard is None:
            self.dashboard = DashboardScreen(
                self.root,
                self.title_font,
                self.normal_font,
                self.button_font,
                username,
                self,
            )
        else:
            self.dashboard.username = username

        self.dashboard.show_dashboard()

    def logout(self):
        if messagebox.askyesno("Logout", "Deseja realmente sair da sua conta?"):
            self.current_user = None
            self.show_main_menu()


def open_sheet_editor(
    root,
    parent_frame,
    file_manager,
    current_user,
    filename,
    content,
    return_callback=None,
    refresh_callback=None,
):
    for widget in parent_frame.winfo_children():
        widget.destroy()

    root.title(f"Editor de Planilha - {filename}")

    user_data = load_user_data()
    can_write = user_data[current_user]["permissions"].get("escrita", False)
    read_only = not can_write

    editor_frame = tk.Frame(parent_frame, bg="#f5f5f5")
    editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    header_frame = tk.Frame(editor_frame, bg="#2c3e50", padx=10, pady=5)
    header_frame.pack(fill=tk.X, pady=(0, 10))

    tk.Label(
        header_frame,
        text=f"Planilha: {filename}",
        fg="white",
        bg="#2c3e50",
        font=("Arial", 10, "bold"),
    ).pack(side=tk.LEFT)

    if read_only:
        tk.Label(
            header_frame,
            text="Modo somente leitura",
            fg="#f39c12",
            bg="#2c3e50",
            font=("Arial", 9),
        ).pack(side=tk.LEFT, padx=10)

    if read_only:
        readonly_frame = tk.Frame(editor_frame, bg="#ffeaa7", padx=10, pady=5)
        readonly_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            readonly_frame,
            text="⚠️ Arquivo aberto em modo somente leitura. Você não tem permissão para editar.",
            bg="#ffeaa7",
            fg="#d35400",
        ).pack(anchor="w")

    sheet_data = {"rows": 10, "columns": 5, "cells": {}}

    if content.strip():
        try:
            sheet_data = json.loads(content)
        except json.JSONDecodeError:
            sheet_data = {"rows": 10, "columns": 5, "cells": {}}

    if sheet_data["rows"] < 5:
        sheet_data["rows"] = 5
    if sheet_data["columns"] < 3:
        sheet_data["columns"] = 3

    tools_frame = tk.Frame(editor_frame, bg="#ecf0f1", padx=10, pady=5)
    tools_frame.pack(fill=tk.X, pady=(0, 10))

    def add_row():
        if not can_write:
            return
        sheet_data["rows"] += 1
        refresh_sheet()

    def add_column():
        if not can_write:
            return
        sheet_data["columns"] += 1
        refresh_sheet()

    tk.Button(
        tools_frame,
        text="+ Linha",
        command=add_row,
        state=tk.NORMAL if can_write else tk.DISABLED,
    ).pack(side=tk.LEFT, padx=5)
    tk.Button(
        tools_frame,
        text="+ Coluna",
        command=add_column,
        state=tk.NORMAL if can_write else tk.DISABLED,
    ).pack(side=tk.LEFT, padx=5)

    sheet_container = tk.Frame(editor_frame)
    sheet_container.pack(fill=tk.BOTH, expand=True, pady=5)

    h_scrollbar = tk.Scrollbar(sheet_container, orient=tk.HORIZONTAL)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    v_scrollbar = tk.Scrollbar(sheet_container)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas = tk.Canvas(sheet_container, bg="white")
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    h_scrollbar.config(command=canvas.xview)
    v_scrollbar.config(command=canvas.yview)
    canvas.config(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

    sheet_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=sheet_frame, anchor="nw", tags="sheet_frame")

    cell_widgets = {}

    def update_cell_value(event, row, col):
        if not can_write:
            return
        widget = event.widget
        value = widget.get()

        cell_id = f"{row},{col}"
        sheet_data["cells"][cell_id] = value

    def refresh_sheet():
        for widget in sheet_frame.winfo_children():
            widget.destroy()
        cell_widgets.clear()

        tk.Label(
            sheet_frame, text="", width=4, bg="#ecf0f1", relief=tk.RIDGE, borderwidth=1
        ).grid(row=0, column=0, sticky="nsew")
        for col in range(sheet_data["columns"]):
            col_label = chr(65 + col) if col < 26 else f"A{chr(65 + col - 26)}"
            tk.Label(
                sheet_frame,
                text=col_label,
                width=10,
                bg="#ecf0f1",
                relief=tk.RIDGE,
                borderwidth=1,
                font=("Arial", 9, "bold"),
            ).grid(row=0, column=col + 1, sticky="nsew")

        for row in range(sheet_data["rows"]):
            tk.Label(
                sheet_frame,
                text=str(row + 1),
                width=4,
                bg="#ecf0f1",
                relief=tk.RIDGE,
                borderwidth=1,
                font=("Arial", 9, "bold"),
            ).grid(row=row + 1, column=0, sticky="nsew")

        for row in range(sheet_data["rows"]):
            for col in range(sheet_data["columns"]):
                cell_id = f"{row},{col}"
                value = sheet_data["cells"].get(cell_id, "")

                if can_write:
                    entry = tk.Entry(
                        sheet_frame, width=10, relief=tk.SUNKEN, borderwidth=1
                    )
                    entry.insert(0, value)
                    entry.bind(
                        "<FocusOut>", lambda e, r=row, c=col: update_cell_value(e, r, c)
                    )
                    entry.bind(
                        "<Return>", lambda e, r=row, c=col: update_cell_value(e, r, c)
                    )
                else:
                    entry = tk.Entry(
                        sheet_frame,
                        width=10,
                        relief=tk.SUNKEN,
                        borderwidth=1,
                        state="readonly",
                    )
                    entry.insert(0, value)

                entry.grid(row=row + 1, column=col + 1, sticky="nsew")
                cell_widgets[cell_id] = entry

        sheet_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    refresh_sheet()

    def on_canvas_configure(event):
        canvas.config(scrollregion=canvas.bbox("all"))

    sheet_frame.bind("<Configure>", on_canvas_configure)

    actions_frame = tk.Frame(editor_frame, bg="#f5f5f5", pady=10)
    actions_frame.pack(fill=tk.X)

    def save_sheet():
        if not can_write:
            messagebox.showerror(
                "Sem permissão", "Você não tem permissão para salvar planilhas."
            )
            return

        try:
            sheet_json = json.dumps(sheet_data, indent=2)

            if filename in file_manager.list_files():
                result, msg = file_manager.edit_file(filename, sheet_json)
            else:
                result, msg = file_manager.create_file(filename, sheet_json)

            if result:
                messagebox.showinfo("Sucesso", msg)
                try:
                    if refresh_callback and callable(refresh_callback):
                        refresh_callback()
                except Exception as e:
                    print(f"[Aviso] Erro ao chamar refresh_callback: {e}")

                try:
                    root.title(f"Editor de Planilha - {filename} (Salvo)")
                except tk.TclError:
                    print(
                        "[Aviso] Não foi possível atualizar o título - widget destruído"
                    )
            else:
                messagebox.showerror("Erro", msg)
        except Exception as e:
            messagebox.showerror("Erro ao salvar", f"Ocorreu um erro: {str(e)}")

    def safe_return():
        try:
            if return_callback and callable(return_callback):
                return_callback()
        except Exception as e:
            print(f"[Erro] Não foi possível voltar à tela anterior: {e}")
            try:
                root.destroy()
            except:
                pass

    tk.Button(
        actions_frame,
        text="Voltar",
        command=safe_return,
        bg="#3498db",
        fg="white",
        width=10,
        pady=5,
    ).pack(side=tk.LEFT, padx=5)

    if can_write:
        tk.Button(
            actions_frame,
            text="Salvar",
            command=save_sheet,
            bg="#2ecc71",
            fg="white",
            width=10,
            pady=5,
        ).pack(side=tk.RIGHT, padx=5)

    return editor_frame


def open_file_editor(
    root,
    parent_frame,
    file_manager,
    current_user,
    filename,
    content,
    return_callback=None,
    refresh_callback=None,
):
    for widget in parent_frame.winfo_children():
        widget.destroy()

    root.title(f"Editor - {filename}")

    user_data = load_user_data()
    can_write = user_data[current_user]["permissions"].get("escrita", False)
    read_only = not can_write

    editor_frame = tk.Frame(parent_frame, bg="#f5f5f5")
    editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    header_frame = tk.Frame(editor_frame, bg="#2c3e50", padx=10, pady=5)
    header_frame.pack(fill=tk.X, pady=(0, 10))

    tk.Label(
        header_frame,
        text=f"Arquivo: {filename}",
        fg="white",
        bg="#2c3e50",
        font=("Arial", 10, "bold"),
    ).pack(side=tk.LEFT)

    if read_only:
        tk.Label(
            header_frame,
            text="Modo somente leitura",
            fg="#f39c12",
            bg="#2c3e50",
            font=("Arial", 9),
        ).pack(side=tk.LEFT, padx=10)

    if read_only:
        readonly_frame = tk.Frame(editor_frame, bg="#ffeaa7", padx=10, pady=5)
        readonly_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            readonly_frame,
            text="⚠️ Arquivo aberto em modo somente leitura. Você não tem permissão para editar.",
            bg="#ffeaa7",
            fg="#d35400",
        ).pack(anchor="w")

    text_editor = scrolledtext.ScrolledText(
        editor_frame, wrap=tk.WORD, font=("Courier", 11)
    )
    text_editor.pack(fill=tk.BOTH, expand=True)
    text_editor.insert(tk.END, content)

    if read_only:
        text_editor.config(state=tk.DISABLED)

    def save():
        if not can_write:
            messagebox.showerror(
                "Sem permissão", "Você não tem permissão para salvar arquivos."
            )
            return

        if filename in file_manager.list_files():
            result, msg = file_manager.edit_file(
                filename, text_editor.get("1.0", tk.END)
            )
        else:
            result, msg = file_manager.create_file(
                filename, text_editor.get("1.0", tk.END)
            )

        if result:
            messagebox.showinfo("Sucesso", msg)
            try:
                if refresh_callback and callable(refresh_callback):
                    refresh_callback()
            except Exception as e:
                print(f"[Aviso] Erro ao chamar refresh_callback: {e}")

            try:
                root.title(f"Editor - {filename} (Salvo)")
            except tk.TclError:
                print("[Aviso] Não foi possível atualizar o título - widget destruído")
        else:
            messagebox.showerror("Erro", msg)

    button_frame = tk.Frame(editor_frame, bg="#f5f5f5", pady=10)
    button_frame.pack(fill=tk.X)

    def safe_return():
        try:
            if return_callback and callable(return_callback):
                return_callback()
        except Exception as e:
            print(f"[Erro] Não foi possível voltar à tela anterior: {e}")
            try:
                root.destroy()
            except:
                pass

    tk.Button(
        button_frame,
        text="Voltar",
        command=safe_return,
        bg="#3498db",
        fg="white",
        width=10,
        pady=5,
    ).pack(side=tk.LEFT, padx=5)

    if can_write:
        tk.Button(
            button_frame,
            text="Salvar",
            command=save,
            bg="#2ecc71",
            fg="white",
            width=10,
            pady=5,
        ).pack(side=tk.RIGHT, padx=5)

    return editor_frame


def open_draw_editor(
    root,
    parent_frame,
    file_manager,
    current_user,
    filename,
    content,
    return_callback=None,
    refresh_callback=None,
):
    for widget in parent_frame.winfo_children():
        widget.destroy()

    root.title(f"Editor de Desenho - {filename}")

    user_data = load_user_data()
    can_write = user_data[current_user]["permissions"].get("escrita", False)
    read_only = not can_write

    editor_frame = tk.Frame(parent_frame, bg="#f5f5f5")
    editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    header_frame = tk.Frame(editor_frame, bg="#2c3e50", padx=10, pady=5)
    header_frame.pack(fill=tk.X, pady=(0, 10))

    tk.Label(
        header_frame,
        text=f"Desenho: {filename}",
        fg="white",
        bg="#2c3e50",
        font=("Arial", 10, "bold"),
    ).pack(side=tk.LEFT)

    if read_only:
        tk.Label(
            header_frame,
            text="Modo somente visualização",
            fg="#f39c12",
            bg="#2c3e50",
            font=("Arial", 9),
        ).pack(side=tk.LEFT, padx=10)

    if read_only:
        readonly_frame = tk.Frame(editor_frame, bg="#ffeaa7", padx=10, pady=5)
        readonly_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            readonly_frame,
            text="⚠️ Arquivo aberto em modo somente visualização. Você não tem permissão para editar.",
            bg="#ffeaa7",
            fg="#d35400",
        ).pack(anchor="w")

    draw_data = {"strokes": [], "current_stroke": []}

    if content.strip():
        try:
            draw_data = json.loads(content)
        except json.JSONDecodeError:
            draw_data = {"strokes": [], "current_stroke": []}

    tools_frame = tk.Frame(editor_frame, bg="#ecf0f1", padx=10, pady=5)
    tools_frame.pack(fill=tk.X, pady=(0, 10))

    color_var = tk.StringVar(value="#000000")
    size_var = tk.IntVar(value=2)
    tool_var = tk.StringVar(value="pencil")

    tk.Label(tools_frame, text="Ferramenta:", bg="#ecf0f1").pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(
        tools_frame,
        text="Lápis",
        variable=tool_var,
        value="pencil",
        bg="#ecf0f1",
        state=tk.NORMAL if can_write else tk.DISABLED,
    ).pack(side=tk.LEFT)
    tk.Radiobutton(
        tools_frame,
        text="Borracha",
        variable=tool_var,
        value="eraser",
        bg="#ecf0f1",
        state=tk.NORMAL if can_write else tk.DISABLED,
    ).pack(side=tk.LEFT)

    tk.Label(tools_frame, text="Cor:", bg="#ecf0f1").pack(side=tk.LEFT, padx=(15, 5))
    color_btn = tk.Button(
        tools_frame,
        bg=color_var.get(),
        width=2,
        height=1,
        state=tk.NORMAL if can_write else tk.DISABLED,
    )
    color_btn.pack(side=tk.LEFT, padx=5)

    def choose_color():
        from tkinter import colorchooser

        color = colorchooser.askcolor(color=color_var.get())[1]
        if color:
            color_var.set(color)
            color_btn.configure(bg=color)

    color_btn.configure(command=choose_color)

    tk.Label(tools_frame, text="Espessura:", bg="#ecf0f1").pack(
        side=tk.LEFT, padx=(15, 5)
    )
    tk.Scale(
        tools_frame,
        variable=size_var,
        from_=1,
        to=10,
        orient=tk.HORIZONTAL,
        length=100,
        bg="#ecf0f1",
        state=tk.NORMAL if can_write else tk.DISABLED,
    ).pack(side=tk.LEFT)

    canvas_frame = tk.Frame(editor_frame, bg="white", bd=2, relief=tk.SUNKEN)
    canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)

    canvas = tk.Canvas(canvas_frame, bg="white", cursor="pencil", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    drawing = False

    def start_drawing(event):
        nonlocal drawing
        if not can_write:
            return
        drawing = True
        draw_data["current_stroke"] = [
            {
                "x": event.x,
                "y": event.y,
                "color": color_var.get() if tool_var.get() == "pencil" else "#FFFFFF",
                "size": size_var.get(),
                "tool": tool_var.get(),
            }
        ]

    def draw(event):
        if not drawing or not can_write:
            return
        x, y = event.x, event.y

        last_point = draw_data["current_stroke"][-1]
        x1, y1 = last_point["x"], last_point["y"]
        color = color_var.get() if tool_var.get() == "pencil" else "#FFFFFF"
        size = size_var.get()

        canvas.create_line(
            x1,
            y1,
            x,
            y,
            fill=color,
            width=size,
            capstyle=tk.ROUND,
            smooth=True,
            splinesteps=36,
        )

        draw_data["current_stroke"].append(
            {"x": x, "y": y, "color": color, "size": size, "tool": tool_var.get()}
        )

    def stop_drawing(event):
        nonlocal drawing
        if not drawing or not can_write:
            return
        drawing = False

        if len(draw_data["current_stroke"]) > 1:
            draw_data["strokes"].append(draw_data["current_stroke"].copy())
        draw_data["current_stroke"] = []

    def clear_canvas():
        if messagebox.askyesno(
            "Limpar Tela", "Deseja realmente limpar todo o desenho?"
        ):
            canvas.delete("all")
            draw_data["strokes"] = []
            draw_data["current_stroke"] = []

    if can_write:
        canvas.bind("<Button-1>", start_drawing)
        canvas.bind("<B1-Motion>", draw)
        canvas.bind("<ButtonRelease-1>", stop_drawing)

    def redraw_canvas():
        canvas.delete("all")
        for stroke in draw_data["strokes"]:
            if len(stroke) < 2:
                continue

            for i in range(len(stroke) - 1):
                pt1 = stroke[i]
                pt2 = stroke[i + 1]
                canvas.create_line(
                    pt1["x"],
                    pt1["y"],
                    pt2["x"],
                    pt2["y"],
                    fill=pt1["color"],
                    width=pt1["size"],
                    capstyle=tk.ROUND,
                    smooth=True,
                    splinesteps=36,
                )

    redraw_canvas()

    actions_frame = tk.Frame(editor_frame, bg="#f5f5f5", pady=10)
    actions_frame.pack(fill=tk.X)

    tk.Button(
        actions_frame,
        text="Limpar Tela",
        command=clear_canvas,
        bg="#e74c3c",
        fg="white",
        width=10,
        pady=5,
        state=tk.NORMAL if can_write else tk.DISABLED,
    ).pack(side=tk.LEFT, padx=5)

    def save_drawing():
        if not can_write:
            messagebox.showerror(
                "Sem permissão", "Você não tem permissão para salvar desenhos."
            )
            return

        try:
            drawing_json = json.dumps(draw_data, indent=2)

            if filename in file_manager.list_files():
                result, msg = file_manager.edit_file(filename, drawing_json)
            else:
                result, msg = file_manager.create_file(filename, drawing_json)

            if result:
                messagebox.showinfo("Sucesso", msg)
                try:
                    if refresh_callback and callable(refresh_callback):
                        refresh_callback()
                except Exception as e:
                    print(f"[Aviso] Erro ao chamar refresh_callback: {e}")

                try:
                    root.title(f"Editor de Desenho - {filename} (Salvo)")
                except tk.TclError:
                    print(
                        "[Aviso] Não foi possível atualizar o título - widget destruído"
                    )
            else:
                messagebox.showerror("Erro", msg)
        except Exception as e:
            messagebox.showerror("Erro ao salvar", f"Ocorreu um erro: {str(e)}")

    def safe_return():
        try:
            if return_callback and callable(return_callback):
                return_callback()
        except Exception as e:
            print(f"[Erro] Não foi possível voltar à tela anterior: {e}")
            try:
                root.destroy()
            except:
                pass

    tk.Button(
        actions_frame,
        text="Voltar",
        command=safe_return,
        bg="#3498db",
        fg="white",
        width=10,
        pady=5,
    ).pack(side=tk.LEFT, padx=5)

    if can_write:
        tk.Button(
            actions_frame,
            text="Salvar",
            command=save_drawing,
            bg="#2ecc71",
            fg="white",
            width=10,
            pady=5,
        ).pack(side=tk.RIGHT, padx=5)

    return editor_frame


def load_user_data():
    try:
        directory = os.path.dirname(USER_DATA_FILE)
        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "w") as file:
                json.dump({}, file, indent=4)
            return {}

        if os.path.getsize(USER_DATA_FILE) == 0:
            with open(USER_DATA_FILE, "w") as file:
                json.dump({}, file, indent=4)
            return {}

        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(
            f"Erro: Arquivo de dados corrompido. Criando backup e iniciando novo arquivo. Erro: {e}"
        )
        if os.path.exists(USER_DATA_FILE):
            backup_name = USER_DATA_FILE + f".bak.{int(time.time())}"
            os.rename(USER_DATA_FILE, backup_name)
        with open(USER_DATA_FILE, "w") as file:
            json.dump({}, file, indent=4)
        return {}
    except Exception as e:
        print(f"Erro ao acessar arquivo de dados: {str(e)}")
        directory = os.path.dirname(USER_DATA_FILE)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(USER_DATA_FILE, "w") as file:
            json.dump({}, file, indent=4)
        return {}


def save_user_data(user_data):
    try:
        directory = os.path.dirname(USER_DATA_FILE)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(USER_DATA_FILE, "w") as file:
            json.dump(user_data, file, indent=4)
    except Exception as e:
        print(f"Erro ao salvar dados do usuário: {e}")
        raise e


def check_account_locked(username):
    user_data = load_user_data()
    if username not in user_data:
        return False
    security = user_data[username].get("security", {})
    if not security.get("is_locked", False):
        return False
    lock_time_str = security.get("lock_time")
    if lock_time_str:
        lock_time = datetime.strptime(lock_time_str, "%Y-%m-%d %H:%M:%S")
        unlock_time = lock_time + timedelta(minutes=LOCK_DURATION_MINUTES)
        if datetime.now() > unlock_time:
            user_data[username]["security"]["is_locked"] = False
            user_data[username]["security"]["failed_attempts"] = 0
            save_user_data(user_data)
            return False
    return True


def reset_failed_attempts(username):
    user_data = load_user_data()
    if username in user_data and "security" in user_data[username]:
        user_data[username]["security"]["failed_attempts"] = 0
        save_user_data(user_data)


def increment_failed_attempts(username):
    user_data = load_user_data()
    if username not in user_data:
        return 0
    if "security" not in user_data[username]:
        user_data[username]["security"] = {
            "failed_attempts": 0,
            "is_locked": False,
            "lock_time": None,
        }
    user_data[username]["security"]["failed_attempts"] += 1
    attempts = user_data[username]["security"]["failed_attempts"]
    if attempts >= MAX_LOGIN_ATTEMPTS:
        user_data[username]["security"]["is_locked"] = True
        user_data[username]["security"]["lock_time"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    save_user_data(user_data)
    return attempts


class FileManager:
    def __init__(self, folder="data/arquivos"):
        self.folder = folder
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        print(f"Gerenciador de arquivos inicializado na pasta: {self.folder}")

    def _validate_filename(self, filename):
        if not filename or ".." in filename or "/" in filename or "\\" in filename:
            return False
        return True

    def list_files(self):
        try:
            return os.listdir(self.folder)
        except Exception as e:
            print(f"Erro ao listar arquivos: {str(e)}")
            return []

    def create_file(self, filename, content=""):
        if not self._validate_filename(filename):
            return False, "Nome de arquivo inválido ou inseguro."

        filepath = os.path.join(self.folder, filename)
        if os.path.exists(filepath):
            return (
                False,
                f"O arquivo '{filename}' já existe. Use a função edit_file para modificá-lo.",
            )

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Arquivo criado: {filename}")
            return True, f"Arquivo '{filename}' criado com sucesso."
        except Exception as e:
            print(f"Erro ao criar arquivo {filename}: {str(e)}")
            return False, str(e)

    def read_file(self, filename):
        if not self._validate_filename(filename):
            return False, "Nome de arquivo inválido ou inseguro."

        filepath = os.path.join(self.folder, filename)
        if not os.path.exists(filepath):
            return False, "Arquivo não encontrado."

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"Arquivo lido: {filename}")
            return True, content
        except Exception as e:
            print(f"Erro ao ler arquivo {filename}: {str(e)}")
            return False, str(e)

    def edit_file(self, filename, content):
        if not self._validate_filename(filename):
            return False, "Nome de arquivo inválido ou inseguro."

        filepath = os.path.join(self.folder, filename)
        if not os.path.exists(filepath):
            return False, "Arquivo não encontrado."

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Arquivo editado: {filename}")
            return True, f"Arquivo '{filename}' editado com sucesso."
        except Exception as e:
            print(f"Erro ao editar arquivo {filename}: {str(e)}")
            return False, str(e)

    def remove_file(self, filename):
        if not self._validate_filename(filename):
            return False, "Nome de arquivo inválido ou inseguro."

        filepath = os.path.join(self.folder, filename)
        if not os.path.exists(filepath):
            return False, "Arquivo não encontrado."

        try:
            os.remove(filepath)
            print(f"Arquivo removido: {filename}")
            return True, f"Arquivo '{filename}' removido com sucesso."
        except Exception as e:
            print(f"Erro ao remover arquivo {filename}: {str(e)}")
            return False, str(e)


def initialize_credentials():
    directory = os.path.dirname(CREDENTIALS_FILE)
    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        if not os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE, "w") as file:
                json.dump({}, file, indent=4)
        else:
            with open(CREDENTIALS_FILE, "r") as file:
                try:
                    json.load(file)
                except json.JSONDecodeError:
                    print(f"Arquivo de credenciais corrompido. Criando backup.")
                    backup_name = CREDENTIALS_FILE + f".bak.{int(time.time())}"
                    os.rename(CREDENTIALS_FILE, backup_name)
                    with open(CREDENTIALS_FILE, "w") as new_file:
                        json.dump({}, new_file, indent=4)
    except Exception as e:
        print(f"Erro ao inicializar credenciais: {e}")
        with open(CREDENTIALS_FILE, "w") as file:
            json.dump({}, file, indent=4)


def load_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        initialize_credentials()

    try:
        with open(CREDENTIALS_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("Erro ao decodificar arquivo de credenciais. Inicializando novo arquivo.")
        initialize_credentials()
        return {}
    except Exception as e:
        print(f"Erro ao carregar credenciais: {e}")
        return {}


def save_credentials(credentials):
    directory = os.path.dirname(CREDENTIALS_FILE)
    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        with open(CREDENTIALS_FILE, "w") as file:
            json.dump(credentials, file, indent=4)
    except Exception as e:
        print(f"Erro ao salvar credenciais: {e}")
        raise e


def register_user(username, password, permissions):
    if len(password) < 6:
        return False, "Senha muito curta. Use pelo menos 6 caracteres."

    credentials = load_credentials()
    if username in credentials:
        return False, "Usuário já existe!"

    salt = generate_salt()
    password_hash = hash_password(password, salt)
    credentials[username] = {"password": password_hash, "salt": salt}
    save_credentials(credentials)

    user_data = load_user_data()
    if permissions is None:
        permissions = {"leitura": False, "escrita": False, "remocao": False}

    user_data[username] = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": "",
        "login_count": 0,
        "notes": [],
        "settings": {"theme": "light"},
        "security": {"failed_attempts": 0, "is_locked": False, "lock_time": None},
        "permissions": permissions,
    }
    save_user_data(user_data)
    return True, f"Usuário '{username}' registrado com sucesso!"


def authenticate_user(username, password):
    print(f"[{datetime.now()}] Tentativa de login: {username}")

    credentials = load_credentials()

    if check_account_locked(username):
        print(f"[{datetime.now()}] Login bloqueado: {username}")
        return False, AUTH_LOCKED

    if username in credentials:
        password_matched = False
        user_record = credentials[username]

        if isinstance(user_record, dict):
            if "salt" in user_record:
                stored_hash = user_record["password"]
                stored_salt = user_record["salt"]
                password_matched = verify_password(stored_hash, stored_salt, password)
            else:
                stored_password = user_record["password"]
                salt = generate_salt()
                password_hash = hash_password(stored_password, salt)
                credentials[username] = {"password": password_hash, "salt": salt}
                save_credentials(credentials)
                password_matched = stored_password == password
        else:
            stored_password = user_record
            salt = generate_salt()
            password_hash = hash_password(stored_password, salt)
            credentials[username] = {"password": password_hash, "salt": salt}
            save_credentials(credentials)
            password_matched = stored_password == password

        if password_matched:
            user_data = load_user_data()
            if username in user_data:
                user_data[username]["last_login"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                user_data[username]["login_count"] += 1
                save_user_data(user_data)

            reset_failed_attempts(username)
            print(f"[{datetime.now()}] Login bem-sucedido: {username}")
            return True, AUTH_SUCCESS

        attempts = increment_failed_attempts(username)
        remaining = MAX_LOGIN_ATTEMPTS - attempts
        print(
            f"[{datetime.now()}] Senha incorreta para {username}. Restantes: {remaining}"
        )

        if remaining <= 0:
            return False, AUTH_LOCKED
        else:
            return False, f"{AUTH_WRONG_PASSWORD}:{remaining}"

    print(f"[{datetime.now()}] Usuário não encontrado: {username}")
    return False, AUTH_NOT_FOUND


if __name__ == "__main__":
    main()
