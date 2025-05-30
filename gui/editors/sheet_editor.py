import tkinter as tk
import json
from tkinter import ttk, messagebox, simpledialog
from core.user_data import load_user_data

def open_sheet_editor(root, parent_frame, file_manager, current_user, filename, content, 
                     return_callback=None, refresh_callback=None):
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
    
    sheet_data = {
        "rows": 10,
        "columns": 5,
        "cells": {}
    }
    
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
    
    tk.Button(tools_frame, text="+ Linha", command=add_row, 
             state=tk.NORMAL if can_write else tk.DISABLED).pack(side=tk.LEFT, padx=5)
    tk.Button(tools_frame, text="+ Coluna", command=add_column,
             state=tk.NORMAL if can_write else tk.DISABLED).pack(side=tk.LEFT, padx=5)
    
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
    canvas.create_window((0, 0), window=sheet_frame, anchor='nw', tags='sheet_frame')
    
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
        
        tk.Label(sheet_frame, text="", width=4, bg="#ecf0f1", relief=tk.RIDGE, 
                 borderwidth=1).grid(row=0, column=0, sticky="nsew")
        for col in range(sheet_data["columns"]):
            col_label = chr(65 + col) if col < 26 else f"A{chr(65 + col - 26)}"
            tk.Label(sheet_frame, text=col_label, width=10, bg="#ecf0f1", relief=tk.RIDGE, 
                    borderwidth=1, font=('Arial', 9, 'bold')).grid(row=0, column=col + 1, sticky="nsew")
        
        for row in range(sheet_data["rows"]):
            tk.Label(sheet_frame, text=str(row + 1), width=4, bg="#ecf0f1", relief=tk.RIDGE, 
                    borderwidth=1, font=('Arial', 9, 'bold')).grid(row=row + 1, column=0, sticky="nsew")
            
        for row in range(sheet_data["rows"]):
            for col in range(sheet_data["columns"]):
                cell_id = f"{row},{col}"
                value = sheet_data["cells"].get(cell_id, "")
                
                if can_write:
                    entry = tk.Entry(sheet_frame, width=10, relief=tk.SUNKEN, borderwidth=1)
                    entry.insert(0, value)
                    entry.bind("<FocusOut>", lambda e, r=row, c=col: update_cell_value(e, r, c))
                    entry.bind("<Return>", lambda e, r=row, c=col: update_cell_value(e, r, c))
                else:
                    entry = tk.Entry(sheet_frame, width=10, relief=tk.SUNKEN, borderwidth=1, 
                                    state="readonly")
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
            messagebox.showerror("Sem permissão", "Você não tem permissão para salvar planilhas.")
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
                    print("[Aviso] Não foi possível atualizar o título - widget destruído")
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
        pady=5
    ).pack(side=tk.LEFT, padx=5)
    
    if can_write:
        tk.Button(
            actions_frame,
            text="Salvar",
            command=save_sheet,
            bg="#2ecc71",
            fg="white",
            width=10,
            pady=5
        ).pack(side=tk.RIGHT, padx=5)
    
    return editor_frame
