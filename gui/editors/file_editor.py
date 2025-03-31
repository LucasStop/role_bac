import tkinter as tk
from tkinter import scrolledtext, messagebox
from core.user_data import load_user_data

def open_file_editor(root, parent_frame, file_manager, current_user, filename, content, 
                    return_callback=None, refresh_callback=None):
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
    
    if read_only:
        readonly_frame = tk.Frame(editor_frame, bg="#ffeaa7", padx=10, pady=5)
        readonly_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            readonly_frame,
            text="⚠️ Arquivo aberto em modo somente leitura. Você não tem permissão para editar.",
            bg="#ffeaa7",
            fg="#d35400"
        ).pack(anchor='w')
    
    text_editor = scrolledtext.ScrolledText(
        editor_frame, 
        wrap=tk.WORD, 
        font=('Courier', 11)
    )
    text_editor.pack(fill=tk.BOTH, expand=True)
    text_editor.insert(tk.END, content)
    
    if read_only:
        text_editor.config(state=tk.DISABLED)
    
    def save():
        if not can_write:
            messagebox.showerror("Sem permissão", "Você não tem permissão para salvar arquivos.")
            return
        
        if filename in file_manager.list_files():
            result, msg = file_manager.edit_file(filename, text_editor.get("1.0", tk.END))
        else:
            result, msg = file_manager.create_file(filename, text_editor.get("1.0", tk.END))
            
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
        pady=5
    ).pack(side=tk.LEFT, padx=5)
    
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
