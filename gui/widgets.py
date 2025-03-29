# gui/widgets.py
import tkinter as tk
from tkinter import font


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
        anchor='w'
    ).pack(side=tk.LEFT)

    tk.Label(
        frame,
        text=value_text,
        font=font.Font(family="Arial", size=9),
        fg="white",
        bg="#34495e",
        anchor='w'
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
        anchor='w'
    ).pack(side=tk.LEFT)

    tk.Label(
        frame,
        text=status_text,
        font=font.Font(family="Arial", size=9, weight="bold"),
        fg=status_color,
        bg="#34495e",
        width=2
    ).pack(side=tk.RIGHT)
