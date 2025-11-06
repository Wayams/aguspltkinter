# frontend/modules/login.py
import customtkinter as ctk
from tkinter import messagebox
from api_client import APIClient

class LoginWindow(ctk.CTkToplevel):
    def __init__(self, master, api_client: APIClient):
        super().__init__(master)
        self.master = master
        self.api_client = api_client
        self.title("Inicio de Sesión")
        self.geometry("400x300")
        self.after(100, self.lift)
        self.transient(master)
        self.grab_set()

        self.user_data = None
        self.build_ui()

    def build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,1,2), weight=1)
        
        ctk.CTkLabel(self, text='Acceso al Sistema', font=('Segoe UI', 18, 'bold')).grid(row=0, column=0, pady=(20, 10))
        
        form_frame = ctk.CTkFrame(self)
        form_frame.grid(row=1, column=0, padx=20, pady=10)
        
        ctk.CTkLabel(form_frame, text="Usuario:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.user_entry = ctk.CTkEntry(form_frame, width=200)
        self.user_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(form_frame, text="Contraseña:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.pwd_entry = ctk.CTkEntry(form_frame, show="*", width=200)
        self.pwd_entry.grid(row=1, column=1, padx=5, pady=5)
        self.pwd_entry.bind('<Return>', lambda event: self.login())

        ctk.CTkButton(self, text="Entrar", command=self.login).grid(row=2, column=0, padx=20, pady=10)

    def login(self):
        username = self.user_entry.get().strip()
        password_str = self.pwd_entry.get().strip()
        
        if not username or not password_str:
            messagebox.showwarning("Datos Incompletos", "El usuario y la contraseña son obligatorios", parent=self)
            return

        try:
            result = self.api_client.login(username, password_str)
            self.user_data = result['user_data']
            self.grab_release()
            self.destroy()
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "incorrectos" in error_msg.lower():
                messagebox.showerror("Error", "Usuario o contraseña incorrectos", parent=self)
            elif "conexión" in error_msg.lower() or "connection" in error_msg.lower():
                messagebox.showerror("Error de Conexión", 
                                    "No se pudo conectar con el servidor.\nAsegúrate de que el backend esté ejecutándose.", 
                                    parent=self)
            else:
                messagebox.showerror("Error", f"Error en el inicio de sesión: {error_msg}", parent=self)

    def destroy(self):
        self.grab_release()
        super().destroy()

