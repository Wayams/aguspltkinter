# frontend/main.py
import customtkinter as ctk
import sys
from ui_main import App

# Configuración recomendada para un aspecto moderno y profesional.
ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")

if __name__ == '__main__':
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"Error principal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

