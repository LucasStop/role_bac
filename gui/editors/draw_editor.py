import tkinter as tk
import json
from tkinter import messagebox, simpledialog
from core.user_data import load_user_data

def open_draw_editor(root, parent_frame, file_manager, current_user, filename, content, 
                     return_callback=None, refresh_callback=None):
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
        font=('Arial', 10, 'bold')
    ).pack(side=tk.LEFT)
    
    if read_only:
        tk.Label(
            header_frame,
            text="Modo somente visualização",
            fg="#f39c12",
            bg="#2c3e50",
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=10)
    
    if read_only:
        readonly_frame = tk.Frame(editor_frame, bg="#ffeaa7", padx=10, pady=5)
        readonly_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            readonly_frame,
            text="⚠️ Arquivo aberto em modo somente visualização. Você não tem permissão para editar.",
            bg="#ffeaa7",
            fg="#d35400"
        ).pack(anchor='w')
    
    draw_data = {
        "strokes": [],
        "current_stroke": []
    }
    
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
    tk.Radiobutton(tools_frame, text="Lápis", variable=tool_var, value="pencil", bg="#ecf0f1",
                  state=tk.NORMAL if can_write else tk.DISABLED).pack(side=tk.LEFT)
    tk.Radiobutton(tools_frame, text="Borracha", variable=tool_var, value="eraser", bg="#ecf0f1",
                  state=tk.NORMAL if can_write else tk.DISABLED).pack(side=tk.LEFT)
    
    tk.Label(tools_frame, text="Cor:", bg="#ecf0f1").pack(side=tk.LEFT, padx=(15, 5))
    color_btn = tk.Button(tools_frame, bg=color_var.get(), width=2, height=1,
                        state=tk.NORMAL if can_write else tk.DISABLED)
    color_btn.pack(side=tk.LEFT, padx=5)
    
    def choose_color():
        from tkinter import colorchooser
        color = colorchooser.askcolor(color=color_var.get())[1]
        if color:
            color_var.set(color)
            color_btn.configure(bg=color)
    
    color_btn.configure(command=choose_color)
    
    tk.Label(tools_frame, text="Espessura:", bg="#ecf0f1").pack(side=tk.LEFT, padx=(15, 5))
    tk.Scale(tools_frame, variable=size_var, from_=1, to=10, orient=tk.HORIZONTAL, length=100,
            bg="#ecf0f1", state=tk.NORMAL if can_write else tk.DISABLED).pack(side=tk.LEFT)
    
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
        draw_data["current_stroke"] = [{
            "x": event.x, 
            "y": event.y,
            "color": color_var.get() if tool_var.get() == "pencil" else "#FFFFFF",
            "size": size_var.get(),
            "tool": tool_var.get()
        }]
        
    def draw(event):
        if not drawing or not can_write:
            return
        x, y = event.x, event.y
        
        last_point = draw_data["current_stroke"][-1]
        x1, y1 = last_point["x"], last_point["y"]
        color = color_var.get() if tool_var.get() == "pencil" else "#FFFFFF"
        size = size_var.get()
        
        canvas.create_line(x1, y1, x, y, fill=color, width=size, 
                          capstyle=tk.ROUND, smooth=True, splinesteps=36)
        
        draw_data["current_stroke"].append({
            "x": x, 
            "y": y,
            "color": color,
            "size": size,
            "tool": tool_var.get()
        })
            
    def stop_drawing(event):
        nonlocal drawing
        if not drawing or not can_write:
            return
        drawing = False
        
        if len(draw_data["current_stroke"]) > 1:
            draw_data["strokes"].append(draw_data["current_stroke"].copy())
        draw_data["current_stroke"] = []
    
    def clear_canvas():
        if messagebox.askyesno("Limpar Tela", "Deseja realmente limpar todo o desenho?"):
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
                    pt1["x"], pt1["y"],
                    pt2["x"], pt2["y"],
                    fill=pt1["color"],
                    width=pt1["size"],
                    capstyle=tk.ROUND,
                    smooth=True,
                    splinesteps=36
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
        state=tk.NORMAL if can_write else tk.DISABLED
    ).pack(side=tk.LEFT, padx=5)
    
    def save_drawing():
        if not can_write:
            messagebox.showerror("Sem permissão", "Você não tem permissão para salvar desenhos.")
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
            command=save_drawing,
            bg="#2ecc71",
            fg="white",
            width=10,
            pady=5
        ).pack(side=tk.RIGHT, padx=5)
    
    return editor_frame
