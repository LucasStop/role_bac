# gui/file_editor.py
import tkinter as tk
from tkinter import scrolledtext, messagebox
from core.user_data import load_user_data


def open_file_editor(parent_root, file_manager, current_user, filename, content, refresh_callback=None):
    """
    Abre uma janela separada para editar o conteúdo de um arquivo.

    Args:
        parent_root: Janela principal Tkinter
        file_manager: Instância de FileManager
        current_user: Nome do usuário logado
        filename: Nome do arquivo a ser editado
        content: Conteúdo atual do arquivo
        refresh_callback: Função opcional para atualizar a lista de arquivos após salvar

    Returns:
        tuple: (success, window ou mensagem de erro)
    """
    editor_window = tk.Toplevel(parent_root)
    editor_window.title(f"Editor - {filename}")
    editor_window.geometry("700x500")
    editor_window.minsize(500, 400)
    editor_window.focus_force()

    user_data = load_user_data()
    can_write = user_data[current_user]["permissions"].get("escrita", False)
    read_only = not can_write

    main_frame = tk.Frame(editor_window)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    if read_only:
        readonly_frame = tk.Frame(main_frame, bg="#ffeaa7", padx=10, pady=5)
        readonly_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            readonly_frame,
            text="⚠️ Arquivo aberto em modo somente leitura. Você não tem permissão para editar.",
            bg="#ffeaa7",
            fg="#d35400"
        ).pack(anchor='w')

    text_editor = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=('Courier', 11))
    text_editor.pack(fill=tk.BOTH, expand=True)
    text_editor.insert(tk.END, content)

    if read_only:
        text_editor.config(state=tk.DISABLED)

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
            editor_window.title(f"Editor - {filename} (Salvo)")
        else:
            messagebox.showerror("Erro", msg)

    button_frame = tk.Frame(main_frame, pady=10)
    button_frame.pack(fill=tk.X)

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

    tk.Button(
        button_frame,
        text="Fechar",
        command=editor_window.destroy,
        bg="#95a5a6",
        fg="white",
        width=10,
        pady=5
    ).pack(side=tk.RIGHT, padx=5)

    return True, editor_window
