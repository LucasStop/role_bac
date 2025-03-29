# gui/file_editor.py
import tkinter as tk
from tkinter import scrolledtext, messagebox
from core.user_data import load_user_data

def open_file_editor(root, parent_frame, file_manager, current_user, filename, content, 
                    return_callback=None, refresh_callback=None):
    """
    Abre o editor de arquivos dentro da janela principal
    
    Args:
        root: Janela principal Tkinter
        parent_frame: Frame pai onde o editor será colocado
        file_manager: Instância de FileManager
        current_user: Nome do usuário logado
        filename: Nome do arquivo a ser editado
        content: Conteúdo atual do arquivo
        return_callback: Função para retornar à tela anterior
        refresh_callback: Função para atualizar a lista de arquivos
    
    Returns:
        Frame do editor
    """
    # Limpar o frame pai
    for widget in parent_frame.winfo_children():
        widget.destroy()
    
    # Atualizar título da janela principal
    root.title(f"Editor - {filename}")
    
    user_data = load_user_data()
    can_write = user_data[current_user]["permissions"].get("escrita", False)
    read_only = not can_write
    
    # Frame principal do editor
    editor_frame = tk.Frame(parent_frame, bg="#f5f5f5")
    editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Cabeçalho com informações e botões
    header_frame = tk.Frame(editor_frame, bg="#2c3e50", padx=10, pady=5)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    
    tk.Label(
        header_frame, 
        text=f"Arquivo: {filename}", 
        fg="white", 
        bg="#2c3e50",
        font=('Arial', 10, 'bold')
    ).pack(side=tk.LEFT)
    
    if read_only:
        tk.Label(
            header_frame,
            text="Modo somente leitura",
            fg="#f39c12",
            bg="#2c3e50",
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=10)
    
    # Área de informação somente leitura, se aplicável
    if read_only:
        readonly_frame = tk.Frame(editor_frame, bg="#ffeaa7", padx=10, pady=5)
        readonly_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            readonly_frame,
            text="⚠️ Arquivo aberto em modo somente leitura. Você não tem permissão para editar.",
            bg="#ffeaa7",
            fg="#d35400"
        ).pack(anchor='w')
    
    # Área de texto com scroll
    text_editor = scrolledtext.ScrolledText(
        editor_frame, 
        wrap=tk.WORD, 
        font=('Courier', 11)
    )
    text_editor.pack(fill=tk.BOTH, expand=True)
    text_editor.insert(tk.END, content)
    
    if read_only:
        text_editor.config(state=tk.DISABLED)
    
    # Função para salvar o arquivo
    def save():
        if not can_write:
            messagebox.showerror("Sem permissão", "Você não tem permissão para salvar arquivos.")
            return
        
        # Se o arquivo já existe, edita-o. Senão, cria um novo.
        if filename in file_manager.list_files():
            result, msg = file_manager.edit_file(filename, text_editor.get("1.0", tk.END))
        else:
            result, msg = file_manager.create_file(filename, text_editor.get("1.0", tk.END))
            
        if result:
            messagebox.showinfo("Sucesso", msg)
            if refresh_callback:
                refresh_callback()
            # Atualizar título mostrando que foi salvo
            root.title(f"Editor - {filename} (Salvo)")
        else:
            messagebox.showerror("Erro", msg)
    
    # Frame de botões
    button_frame = tk.Frame(editor_frame, bg="#f5f5f5", pady=10)
    button_frame.pack(fill=tk.X)
    
    # Botão de voltar à tela anterior
    tk.Button(
        button_frame,
        text="Voltar",
        command=return_callback,
        bg="#3498db",
        fg="white",
        width=10,
        pady=5
    ).pack(side=tk.LEFT, padx=5)
    
    # Botão de salvar (se tiver permissão)
    if can_write:
        tk.Button(
            button_frame,
            text="Salvar",
            command=save,
            bg="#2ecc71",
            fg="white",
            width=10,
            pady=5
        ).pack(side=tk.RIGHT, padx=5)
    
    return editor_frame
