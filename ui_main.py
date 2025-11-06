# frontend/ui_main.py
import customtkinter as ctk
from tkinter import messagebox
from modules.users import UsersWindow
from modules.login import LoginWindow
from api_client import APIClient
import sys

# Importar todos los módulos adaptados
from modules.payments import PaymentsWindow
from modules.reports import ReportsWindow
from modules.admins import AdminsWindow

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Agua SPL")
        self.geometry("1024x768")
        self.minsize(900, 600)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Inicializar cliente API
        self.api_client = APIClient()
        
        self.current_user = None
        self.login_window = None
        self.current_frame = None

        self.show_login()

    def show_login(self):
        """Muestra la ventana de login al inicio."""
        self.login_window = LoginWindow(self, self.api_client)
        self.wait_window(self.login_window)
        
        self.current_user = self.login_window.user_data
        
        if self.current_user and self.current_user.get('Estado', 0) == 1:
            # Inicializar todas las ventanas/frames del sistema
            # Pasar api_client a cada módulo
            self.users_frame = UsersWindow(self, self.api_client)
            
            # Inicializar todos los módulos con api_client
            self.payments_frame = PaymentsWindow(self, self.api_client)
            self.reports_frame = ReportsWindow(self, self.api_client)
            self.admins_frame = AdminsWindow(self, self.current_user, self.api_client)
            
            # Configurar la UI principal
            self.setup_ui()
            
            # Seleccionar el frame inicial
            self.select_frame_by_name("users")
        else:
            messagebox.showerror("Acceso Denegado", "No se pudo iniciar sesión o la cuenta está inactiva. Cerrando el sistema.")
            self.quit()

    def setup_ui(self):
        """Configura el menú de navegación lateral."""
        
        self.navigation_frame = ctk.CTkFrame(self, 
                                             corner_radius=0, 
                                             width=220, 
                                             fg_color="#1E1E1E")
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        
        self.navigation_frame.grid_rowconfigure(5, weight=1)
        self.navigation_frame.grid_rowconfigure(7, weight=0)

        ctk.CTkLabel(self.navigation_frame,
                     text="AGUA SPL",
                     font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.DEFAULT_BUTTON_COLOR = "#3CB3D1"
        self.HOVER_BUTTON_COLOR = "#4EC1E0"
        self.ACTIVE_BUTTON_COLOR = "#1F6AA5"
        self.LOGOUT_COLOR = "#F44336"
        self.LOGOUT_HOVER_COLOR = "#D32F2F"

        common_style = {
            "height": 40,
            "corner_radius": 6,
            "font": ctk.CTkFont(size=14, weight="bold"),
            "anchor": "w",
        }
        
        nav_button_args = {
            **common_style,
            "fg_color": self.DEFAULT_BUTTON_COLOR, 
            "hover_color": self.HOVER_BUTTON_COLOR
        }
        
        self.navigation_buttons = {}
        
        self.navigation_buttons["users"] = ctk.CTkButton(self.navigation_frame,
                                                      text="👤 Suscriptores",
                                                      command=lambda: self.select_frame_by_name("users"),
                                                      **nav_button_args) 
        self.navigation_buttons["users"].grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 5))

        self.navigation_buttons["payments"] = ctk.CTkButton(self.navigation_frame,
                                                         text="💰 Pagos",
                                                         command=lambda: self.select_frame_by_name("payments"),
                                                         **nav_button_args) 
        self.navigation_buttons["payments"].grid(row=2, column=0, sticky="ew", padx=20, pady=5)
        
        self.navigation_buttons["reports"] = ctk.CTkButton(self.navigation_frame,
                                                        text="📈 Reportes",
                                                        command=lambda: self.select_frame_by_name("reports"),
                                                        **nav_button_args) 
        self.navigation_buttons["reports"].grid(row=3, column=0, sticky="ew", padx=20, pady=5)

        if self.current_user['Rol'] == 'Presidente':
            self.navigation_buttons["admins"] = ctk.CTkButton(self.navigation_frame,
                                                             text="🛠️ Administradores",
                                                             command=lambda: self.select_frame_by_name("admins"),
                                                             **nav_button_args) 
            self.navigation_buttons["admins"].grid(row=4, column=0, sticky="ew", padx=20, pady=5)
        
        user_info_frame = ctk.CTkFrame(self.navigation_frame, fg_color="#3A7CB1")
        user_info_frame.grid(row=6, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(user_info_frame, 
                     text="Usuario Activo:",
                     font=('Segoe UI', 10, 'bold'),
                     text_color="#DCE4EE").pack(anchor='w', padx=10, pady=(5, 0))
        
        ctk.CTkLabel(user_info_frame, 
                     text=f"{self.current_user['Nombre']} ({self.current_user['Rol']})",
                     font=('Segoe UI', 12),
                     text_color="white").pack(anchor='w', padx=10, pady=(0, 5))
                     
        ctk.CTkButton(self.navigation_frame,
                      text="🔒 Cerrar Sesión",
                      command=self.logout,
                      **common_style,
                      fg_color=self.LOGOUT_COLOR,
                      hover_color=self.LOGOUT_HOVER_COLOR
                      ).grid(row=7, column=0, sticky="ew", padx=20, pady=(5, 20))

    def select_frame_by_name(self, name):
        """Maneja el cambio de contenido en la vista principal."""
        
        for key, button in self.navigation_buttons.items():
            button.configure(fg_color=self.DEFAULT_BUTTON_COLOR, hover_color=self.HOVER_BUTTON_COLOR) 
            
        if self.current_frame:
            self.current_frame.grid_forget()

        if name == "users":
            self.current_frame = self.users_frame
        elif name == "payments":
            self.current_frame = self.payments_frame
        elif name == "reports":
            self.current_frame = self.reports_frame
            if hasattr(self.reports_frame, 'reset_view'):
                self.reports_frame.reset_view()
        elif name == "admins":
            if self.current_user['Rol'] == 'Presidente':
                self.current_frame = self.admins_frame
                if hasattr(self.admins_frame, 'load_admins'):
                    self.admins_frame.load_admins()
            else:
                return
            
        if self.current_frame:
            self.current_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        if name in self.navigation_buttons:
            self.navigation_buttons[name].configure(fg_color=self.ACTIVE_BUTTON_COLOR, hover_color=self.ACTIVE_BUTTON_COLOR) 

    def logout(self):
        """Cierra la sesión y vuelve a la pantalla de login."""
        if messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que deseas cerrar la sesión actual?"):
            self.api_client.logout()
            self.current_user = None
            
            for widget in self.winfo_children():
                widget.destroy()
            
            self.setup_ui_for_login_restart()
            self.show_login()
            
    def setup_ui_for_login_restart(self):
        """Limpia las referencias a frames."""
        self.current_frame = None
        try:
            del self.users_frame
            del self.payments_frame
            del self.reports_frame
            if hasattr(self, 'admins_frame'):
                del self.admins_frame
        except AttributeError:
            pass

if __name__ == "__main__":
    app = App()
    app.mainloop()

