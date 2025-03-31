import tkinter as tk
from tkinter import messagebox
from core.credentials import initialize_credentials
from gui.auth_screen import AuthScreen
from gui.dashboard_screen import DashboardScreen

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
            response = messagebox.askquestion("Sair", "Você está conectado. Deseja realmente sair?")
            if response == 'yes':
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
