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
            
        # Configurar janela principal para dashboard
        self.root.title(f"Dashboard - {self.current_user}")
        self.root.geometry("800x600")  # Aumentar o tamanho para acomodar mais conteúdo
        
        # Frame principal com 3 painéis
        main_container = tk.Frame(self.root, bg="#f5f5f5")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # === PAINEL SUPERIOR (CABEÇALHO) ===
        header_frame = tk.Frame(main_container, bg="#2c3e50", height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))
        
        # Logo ou título do sistema
        tk.Label(header_frame, text="Sistema de Controle de Acesso", 
                font=font.Font(family="Arial", size=14, weight="bold"),
                fg="white", bg="#2c3e50").pack(side=tk.LEFT, padx=20, pady=15)
        
        # Informações do usuário e botão de logout
        user_frame = tk.Frame(header_frame, bg="#2c3e50")
        user_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(user_frame, text=f"Usuário: {self.current_user}", 
                font=font.Font(family="Arial", size=10),
                fg="white", bg="#2c3e50").pack(side=tk.LEFT, padx=10)
                
        tk.Button(user_frame, text="Sair", command=self.logout,
                  bg="#e74c3c", fg="white", 
                  font=font.Font(family="Arial", size=9)).pack(side=tk.LEFT)
        
        # === PAINÉIS LATERAIS E PRINCIPAL ===
        content_container = tk.Frame(main_container, bg="#f5f5f5")
        content_container.pack(fill=tk.BOTH, expand=True)
        
        # Painel lateral esquerdo (estatísticas e info)
        sidebar_frame = tk.Frame(content_container, bg="#34495e", width=200)
        sidebar_frame.pack(fill=tk.Y, side=tk.LEFT, padx=(0, 10))
        sidebar_frame.pack_propagate(False)  # Impedir que widgets modifiquem o tamanho
        
        # Título do painel lateral
        tk.Label(sidebar_frame, text="Informações", 
                font=font.Font(family="Arial", size=12, weight="bold"),
                fg="white", bg="#34495e").pack(pady=(20, 10), padx=10, anchor='w')
        
        # Carregar dados do usuário
        user_data = load_user_data()
        user_info = user_data.get(self.current_user, {})
        
        # Informações do usuário
        info_frame = tk.Frame(sidebar_frame, bg="#34495e", padx=10, pady=5)
        info_frame.pack(fill=tk.X)
        
        # Informações úteis
        self.create_info_label(info_frame, "Último login:", 
                             user_info.get("last_login", "Primeiro acesso"))
        self.create_info_label(info_frame, "Total de logins:", 
                             str(user_info.get("login_count", "1")))
        self.create_info_label(info_frame, "Conta criada em:", 
                             user_info.get("created_at", "Desconhecido"))
        
        # Separador
        ttk.Separator(sidebar_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Permissões
        tk.Label(sidebar_frame, text="Permissões", 
                font=font.Font(family="Arial", size=12, weight="bold"),
                fg="white", bg="#34495e").pack(pady=(10, 5), padx=10, anchor='w')
        
        permissions = user_info.get("permissions", {})
        self.create_permission_label(sidebar_frame, "Leitura", permissions.get("leitura", False))
        self.create_permission_label(sidebar_frame, "Escrita", permissions.get("escrita", False))
        self.create_permission_label(sidebar_frame, "Remoção", permissions.get("remocao", False))
        
        # Painel principal (arquivos e ações)
        main_panel = tk.Frame(content_container, bg="white")
        main_panel.pack(fill=tk.BOTH, expand=True)
        
        # === BARRA DE AÇÕES ===
        actions_frame = tk.Frame(main_panel, bg="#ecf0f1", height=40, padx=10, pady=10)
        actions_frame.pack(fill=tk.X)
        
        # Rótulo com título da seção
        tk.Label(actions_frame, text="ARQUIVOS DO SISTEMA", 
                font=font.Font(family="Arial", size=12, weight="bold"),
                bg="#ecf0f1").pack(side=tk.LEFT)
                
        # Criar novo arquivo
        new_file_button = tk.Button(
            actions_frame, text="Novo Arquivo", command=self.create_new_file,
            bg="#2ecc71", fg="white", padx=10, 
            state=tk.NORMAL if permissions.get("escrita", False) else tk.DISABLED
        )
        new_file_button.pack(side=tk.RIGHT, padx=5)
        
        # Botão refresh
        refresh_button = tk.Button(
            actions_frame, text="Atualizar Lista", command=self.refresh_file_list,
            bg="#3498db", fg="white", padx=10
        )
        refresh_button.pack(side=tk.RIGHT, padx=5)
        
        # === LISTA DE ARQUIVOS ===
        files_container = tk.Frame(main_panel, bg="white", padx=10, pady=10)
        files_container.pack(fill=tk.BOTH, expand=True)
        
        # Criação de uma Treeview para lista de arquivos com estilo melhorado
        columns = ("nome", "tamanho", "modificado", "permissoes")
        
        self.file_tree = ttk.Treeview(files_container, columns=columns, show="headings", selectmode="browse")
        
        # Configurar cabeçalhos
        self.file_tree.heading("nome", text="Nome do Arquivo")
        self.file_tree.heading("tamanho", text="Tamanho")
        self.file_tree.heading("modificado", text="Última Modificação")
        self.file_tree.heading("permissoes", text="Ações")
        
        # Configurar colunas
        self.file_tree.column("nome", width=250, anchor='w')
        self.file_tree.column("tamanho", width=100, anchor='center')
        self.file_tree.column("modificado", width=150, anchor='center')
        self.file_tree.column("permissoes", width=150, anchor='center')
        
        # Scrollbar para a treeview
        scrollbar = ttk.Scrollbar(files_container, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscroll=scrollbar.set)
        
        # Posicionar elementos
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Associar eventos
        self.file_tree.bind("<Double-1>", lambda event: self.open_selected_file())
        self.file_tree.bind("<Button-3>", self.show_context_menu)  # Menu de contexto com o botão direito
        
        # === BARRA DE STATUS ===
        status_frame = tk.Frame(main_container, bg="#7f8c8d", height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = tk.Label(status_frame, text="Pronto", fg="white", bg="#7f8c8d", anchor='w')
        self.status_label.pack(fill=tk.X, padx=10, pady=3)
        
        # Preencher a lista de arquivos
        self.refresh_file_list()
    
    def create_info_label(self, parent, label_text, value_text):
        frame = tk.Frame(parent, bg="#34495e")
        frame.pack(fill=tk.X, pady=2)
        
        tk.Label(frame, text=label_text, font=font.Font(family="Arial", size=9),
                fg="#bdc3c7", bg="#34495e", width=12, anchor='w').pack(side=tk.LEFT)
                
        tk.Label(frame, text=value_text, font=font.Font(family="Arial", size=9),
                fg="white", bg="#34495e", anchor='w').pack(side=tk.LEFT, padx=5)
    
    def create_permission_label(self, parent, permission_name, has_permission):
        frame = tk.Frame(parent, bg="#34495e", padx=10, pady=2)
        frame.pack(fill=tk.X)
        
        status_color = "#2ecc71" if has_permission else "#e74c3c"
        status_text = "✓" if has_permission else "✗"
        
        tk.Label(frame, text=permission_name + ":", font=font.Font(family="Arial", size=9),
                fg="#bdc3c7", bg="#34495e", anchor='w').pack(side=tk.LEFT)
                
        tk.Label(frame, text=status_text, font=font.Font(family="Arial", size=9, weight="bold"),
                fg=status_color, bg="#34495e", width=2).pack(side=tk.RIGHT)

    def refresh_file_list(self):
        # Limpar lista atual
        for i in self.file_tree.get_children():
            self.file_tree.delete(i)
            
        # Carregar lista de arquivos
        files = self.file_manager.list_files()
        file_count = len(files) if files else 0
        
        if not files:
            self.status_label.config(text="Nenhum arquivo encontrado no sistema.")
            return
            
        user_data = load_user_data()
        permissions = user_data[self.current_user]["permissions"]
        can_read = permissions["leitura"]
        can_write = permissions["escrita"]
        can_delete = permissions["remocao"]
        
        for file in files:
            try:
                # Obter informações do arquivo
                file_path = os.path.join(self.file_manager.folder, file)
                
                # Calcular o tamanho do arquivo de forma legível
                size_bytes = os.path.getsize(file_path)
                size_str = self.format_file_size(size_bytes)
                
                # Obter data de modificação do arquivo
                mod_time = os.path.getmtime(file_path)
                mod_time_str = datetime.fromtimestamp(mod_time).strftime('%d/%m/%Y %H:%M')
                
                # Criar texto de ações disponíveis com base nas permissões
                actions = []
                if can_read:
                    actions.append("Ler")
                if can_write:
                    actions.append("Editar")
                if can_delete:
                    actions.append("Remover")
                actions_str = ", ".join(actions) if actions else "Sem permissões"
                
                # Inserir na lista
                self.file_tree.insert("", tk.END, values=(file, size_str, mod_time_str, actions_str))
            except Exception as e:
                print(f"Erro ao processar arquivo {file}: {str(e)}")
                
        self.status_label.config(text=f"{file_count} arquivo(s) encontrado(s) no sistema")

    def format_file_size(self, size_bytes):
        """Converte tamanho em bytes para formato legível (KB, MB, etc)"""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.1f} GB"

    def show_context_menu(self, event):
        """Exibe menu de contexto ao clicar com botão direito em um arquivo"""
        try:
            # Selecionar item sob o cursor
            item_id = self.file_tree.identify_row(event.y)
            if not item_id:
                return
                
            # Seleciona o item clicado
            self.file_tree.selection_set(item_id)
            self.file_tree.focus(item_id)
            
            # Obter nome do arquivo selecionado
            filename = self.file_tree.item(item_id, "values")[0]
            
            # Verificar permissões do usuário
            user_data = load_user_data()
            permissions = user_data[self.current_user]["permissions"]
            can_read = permissions["leitura"]
            can_write = permissions["escrita"] 
            can_delete = permissions["remocao"]
            
            # Criar menu de contexto
            context_menu = tk.Menu(self.root, tearoff=0)
            
            if can_read:
                context_menu.add_command(label="Abrir", 
                                        command=self.open_selected_file)
                
            if can_write:
                context_menu.add_command(label="Editar", 
                                        command=self.open_selected_file)
                
            if can_delete:
                context_menu.add_separator()
                context_menu.add_command(label="Remover", 
                                        command=self.remove_selected_file,
                                        foreground="#e74c3c")
            
            # Exibir menu no local do clique
            context_menu.tk_popup(event.x_root, event.y_root)
            
        except Exception as e:
            print(f"Erro ao exibir menu de contexto: {str(e)}")

    def create_new_file(self):
        # Verificar permissões
        user_data = load_user_data()
        if not user_data[self.current_user]["permissions"]["escrita"]:
            messagebox.showerror("Sem permissão", "Você não tem permissão para criar arquivos.")
            return
            
        filename = simpledialog.askstring("Novo Arquivo", "Digite o nome do arquivo:")
        if not filename:
            return
            
        # Adicionar extensão .txt se não houver extensão
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
        
        # Verificar permissões
        user_data = load_user_data()
        if not user_data[self.current_user]["permissions"]["leitura"]:
            messagebox.showerror("Sem permissão", "Você não tem permissão para ler arquivos.")
            return
            
        success, content = self.file_manager.read_file(filename)
        if success:
            self.open_file_editor(filename, content)
            self.status_label.config(text=f"Arquivo aberto: {filename}")
        else:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo: {content}")

    def open_file_editor(self, filename, content):
        # Criar uma nova janela para editar o arquivo
        editor_window = tk.Toplevel(self.root)
        editor_window.title(f"Editor - {filename}")
        editor_window.geometry("700x500")
        editor_window.minsize(500, 400)
        editor_window.focus_force()  # Trazer janela para frente
        
        # Verificar permissão de escrita
        user_data = load_user_data()
        can_write = user_data[self.current_user]["permissions"]["escrita"]
        read_only = not can_write
        
        # Frame principal do editor
        main_frame = tk.Frame(editor_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Informação de somente leitura, se aplicável
        if read_only:
            readonly_frame = tk.Frame(main_frame, bg="#ffeaa7", padx=10, pady=5)
            readonly_frame.pack(fill=tk.X, pady=(0, 10))
            tk.Label(readonly_frame, text="⚠️ Arquivo aberto em modo somente leitura. Você não tem permissão para editar.",
                    bg="#ffeaa7", fg="#d35400").pack(anchor='w')
        
        # Área de texto com scroll
        text_editor = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, 
                                              font=('Courier', 11))
        text_editor.pack(fill=tk.BOTH, expand=True)
        text_editor.insert(tk.END, content)
        
        # Se for somente leitura, desabilitar a edição
        if read_only:
            text_editor.config(state=tk.DISABLED)
        
        # Botões de ação
        button_frame = tk.Frame(main_frame, pady=10)
        button_frame.pack(fill=tk.X)
        
        if can_write:
            save_button = tk.Button(
                button_frame, 
                text="Salvar", 
                command=lambda: self.save_file(filename, text_editor.get("1.0", tk.END), editor_window),
                bg="#2ecc71", fg="white", width=10, pady=5
            )
            save_button.pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Fechar", 
            command=editor_window.destroy,
            bg="#95a5a6", fg="white", width=10, pady=5
        ).pack(side=tk.RIGHT, padx=5)
        
        # Atualizar status
        self.status_label.config(text=f"Arquivo aberto para edição: {filename}")
        
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
