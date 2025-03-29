import os
import tkinter as tk
from tkinter import font, ttk, messagebox, scrolledtext, simpledialog
from datetime import datetime

from core.file_manager import FileManager
from core.user_data import load_user_data

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
        
    def show_dashboard(self):
        # Limpar a tela atual
        for widget in self.root.winfo_children():
            widget.destroy()

        # Restaurar o tamanho da janela que pode ter sido alterado pelo editor
        self.root.title(f"Dashboard - {self.username}")
        self.root.geometry("1000x600") 

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

        tk.Label(user_frame, text=f"Usuário: {self.username}",
                 font=font.Font(family="Arial", size=10), fg="white", bg="#2c3e50").pack(side=tk.LEFT, padx=10)
        tk.Button(user_frame, text="Sair", command=self.controller.logout,
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

        user_info = load_user_data().get(self.username, {})

        info_frame = tk.Frame(sidebar, bg="#34495e", padx=10, pady=5)
        info_frame.pack(fill=tk.X)

        self.create_info_label(info_frame, "Último login:", user_info.get("last_login", "Primeiro acesso"))
        self.create_info_label(info_frame, "Total de logins:", str(user_info.get("login_count", "1")))
        self.create_info_label(info_frame, "Conta criada em:", user_info.get("created_at", "Desconhecido"))

        ttk.Separator(sidebar, orient='horizontal').pack(fill=tk.X, pady=10)

        tk.Label(sidebar, text="Permissões",
                 font=font.Font(family="Arial", size=12, weight="bold"),
                 fg="white", bg="#34495e").pack(pady=(10, 5), padx=10, anchor='w')

        permissions = user_info.get("permissions", {})
        self.create_permission_label(sidebar, "Leitura", permissions.get("leitura", False))
        self.create_permission_label(sidebar, "Escrita", permissions.get("escrita", False))
        self.create_permission_label(sidebar, "Remoção", permissions.get("remocao", False))

    def _build_main_panel(self, parent):
        main_panel = tk.Frame(parent, bg="white")
        main_panel.pack(fill=tk.BOTH, expand=True)

        actions_frame = tk.Frame(main_panel, bg="#ecf0f1", height=40, padx=10, pady=10)
        actions_frame.pack(fill=tk.X)

        tk.Label(actions_frame, text="ARQUIVOS DO SISTEMA",
                 font=font.Font(family="Arial", size=12, weight="bold"),
                 bg="#ecf0f1").pack(side=tk.LEFT)

        user_data = load_user_data()
        permissions = user_data[self.username].get("permissions", {})

        tk.Button(actions_frame, text="Novo Arquivo", command=self.create_new_file,
                  bg="#2ecc71", fg="white", padx=10,
                  state=tk.NORMAL if permissions.get("escrita") else tk.DISABLED).pack(side=tk.RIGHT, padx=5)
        
        # Botão para excluir arquivo
        tk.Button(actions_frame, text="Excluir Arquivo", command=self.remove_selected_file,
                  bg="#e74c3c", fg="white", padx=10,
                  state=tk.NORMAL if permissions.get("remocao") else tk.DISABLED).pack(side=tk.RIGHT, padx=5)

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
        
        # Adicionar menu de contexto ao clicar com botão direito
        self.context_menu = tk.Menu(self.file_tree, tearoff=0)
        self.file_tree.bind("<Button-3>", self.show_context_menu)
        
    def show_context_menu(self, event):
        """Exibe o menu de contexto ao clicar com o botão direito em um item"""
        # Primeiro seleciona o item sob o cursor
        item = self.file_tree.identify_row(event.y)
        if item:
            self.file_tree.selection_set(item)
            
            # Limpa o menu de contexto
            self.context_menu.delete(0, tk.END)
            
            # Adiciona as opções com base nas permissões
            user_data = load_user_data()
            permissions = user_data[self.username].get("permissions", {})
            
            if permissions.get("leitura"):
                self.context_menu.add_command(label="Abrir", command=self.open_selected_file)
                
            if permissions.get("escrita"):
                self.context_menu.add_command(label="Editar", command=self.open_selected_file)
                
            if permissions.get("remocao"):
                self.context_menu.add_command(label="Excluir", command=self.remove_selected_file)
                
            # Exibe o menu no local do clique
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def _build_status_bar(self, parent):
        status = tk.Frame(parent, bg="#7f8c8d", height=25)
        status.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = tk.Label(status, text="Pronto", fg="white", bg="#7f8c8d", anchor='w')
        self.status_label.pack(fill=tk.X, padx=10, pady=3)

    def create_info_label(self, parent, label_text, value_text):
        """Cria um label com informação no painel lateral"""
        frame = tk.Frame(parent, bg="#34495e")
        frame.pack(fill=tk.X, pady=2)
        
        tk.Label(frame, text=label_text, font=font.Font(family="Arial", size=9),
                fg="#bdc3c7", bg="#34495e", width=12, anchor='w').pack(side=tk.LEFT)
                
        tk.Label(frame, text=value_text, font=font.Font(family="Arial", size=9),
                fg="white", bg="#34495e", anchor='w').pack(side=tk.LEFT, padx=5)
    
    def create_permission_label(self, parent, permission_name, has_permission):
        """Cria um indicador de permissão no painel lateral"""
        frame = tk.Frame(parent, bg="#34495e", padx=10, pady=2)
        frame.pack(fill=tk.X)
        
        status_color = "#2ecc71" if has_permission else "#e74c3c"
        status_text = "✓" if has_permission else "✗"
        
        tk.Label(frame, text=permission_name + ":", font=font.Font(family="Arial", size=9),
                fg="#bdc3c7", bg="#34495e", anchor='w').pack(side=tk.LEFT)
                
        tk.Label(frame, text=status_text, font=font.Font(family="Arial", size=9, weight="bold"),
                fg=status_color, bg="#34495e", width=2).pack(side=tk.RIGHT)

    def refresh_file_list(self):
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
        """Formata o tamanho do arquivo em unidades legíveis (B, KB, MB, GB)"""
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
        if not user_data[self.username]["permissions"].get("escrita"):
            messagebox.showerror("Sem permissão", "Você não tem permissão para criar arquivos.")
            return

        filename = simpledialog.askstring("Novo Arquivo", "Digite o nome do arquivo:")
        if not filename:
            return

        if "." not in filename:
            filename += ".txt"

        # Aqui verificamos se o arquivo já existe
        if filename in self.file_manager.list_files():
            result, msg = self.file_manager.read_file(filename)
            if result:
                content = msg
            else:
                content = ""
        else:
            # Arquivo não existe, criar novo com conteúdo vazio
            content = ""
            result, msg = self.file_manager.create_file(filename, content)
            if not result:
                messagebox.showerror("Erro", f"Não foi possível criar o arquivo: {msg}")
                return
        
        # Limpar a janela principal e abrir o editor integrado
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Criar um frame principal para armazenar o editor
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Abrir o editor integrado na janela principal
        open_file_editor(
            self.root,
            main_frame,
            self.file_manager,
            self.username,
            filename,
            content,
            self.show_dashboard,  # Função para voltar ao dashboard
            self.refresh_file_list  # Função para atualizar a lista de arquivos
        )
        
        self.status_label.config(text=f"Editando arquivo: {filename}")

    def open_selected_file(self):
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showinfo("Selecione um arquivo", "Por favor, selecione um arquivo para abrir.")
            return

        filename = self.file_tree.item(selection[0], "values")[0]
        user_data = load_user_data()

        if not user_data[self.username]["permissions"].get("leitura"):
            messagebox.showerror("Sem permissão", "Você não tem permissão para ler arquivos.")
            return

        success, content = self.file_manager.read_file(filename)
        if success:
            # Limpar a janela principal e abrir o editor integrado
            for widget in self.root.winfo_children():
                widget.destroy()
                
            # Criar um frame principal para armazenar o editor
            main_frame = tk.Frame(self.root)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Abrir o editor integrado na janela principal
            open_file_editor(
                self.root,
                main_frame,
                self.file_manager,
                self.username,
                filename,
                content,
                self.show_dashboard,  # Função para voltar ao dashboard
                self.refresh_file_list  # Função para atualizar a lista de arquivos
            )
        else:
            messagebox.showerror("Erro", f"Erro ao abrir arquivo: {content}")
            
    def remove_selected_file(self):
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showinfo("Selecione um arquivo", "Por favor, selecione um arquivo para remover.")
            return
            
        filename = self.file_tree.item(selection[0], "values")[0]
        
        user_data = load_user_data()
        if not user_data[self.username]["permissions"].get("remocao"):
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