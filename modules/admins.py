# frontend/modules/admins.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from api_client import APIClient

class AdminsWindow(ctk.CTkFrame):
    def __init__(self, master, current_user, api_client: APIClient):
        super().__init__(master)
        self.current_user = current_user
        self.api_client = api_client
        self.roles_list = ['Presidente', 'Secretario', 'Tesorero', 'Vocal']
        self.configure_treeview_style()
        self.build_ui()
        self.load_admins()

    def configure_treeview_style(self):
        """Configura el estilo visual de la tabla."""
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview",
                       background="#2A2D2E",
                       foreground="#DCE4EE",
                       rowheight=25,
                       fieldbackground="#2A2D2E",
                       borderwidth=0)
        
        style.configure("Treeview.Heading",
                       font=('Segoe UI', 11, 'bold'),
                       background="#3A7CB1",
                       foreground="white",
                       relief="flat")
        
        style.map('Treeview',
                 background=[('selected', '#1F6AA5')],
                 foreground=[('selected', 'white')])

    def build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        ctk.CTkLabel(self, text='Gestión de Administradores', 
                    font=('Segoe UI', 18, 'bold')).grid(row=0, column=0, sticky='w', padx=15, pady=(15, 5))

        # Formulario
        form_frame = ctk.CTkFrame(self)
        form_frame.grid(row=1, column=0, sticky='ew', padx=15, pady=10)
        form_frame.grid_columnconfigure(1, weight=1)
        
        self.id_var = ctk.StringVar()
        self.usuario_var = ctk.StringVar()
        self.nombre_var = ctk.StringVar()
        self.rol_var = ctk.StringVar(value='Presidente')
        self.estado_var = ctk.IntVar(value=1)

        # Campos del formulario
        ctk.CTkLabel(form_frame, text="Usuario:", width=100).grid(row=0, column=0, padx=10, pady=8, sticky='w')
        ctk.CTkEntry(form_frame, textvariable=self.usuario_var, height=35).grid(row=0, column=1, padx=10, pady=8, sticky='ew')

        ctk.CTkLabel(form_frame, text="Nombre:", width=100).grid(row=1, column=0, padx=10, pady=8, sticky='w')
        ctk.CTkEntry(form_frame, textvariable=self.nombre_var, height=35).grid(row=1, column=1, padx=10, pady=8, sticky='ew')

        ctk.CTkLabel(form_frame, text="Rol:", width=100).grid(row=2, column=0, padx=10, pady=8, sticky='w')
        ctk.CTkOptionMenu(form_frame, variable=self.rol_var, values=self.roles_list, height=35).grid(row=2, column=1, padx=10, pady=8, sticky='ew')

        ctk.CTkCheckBox(form_frame, text="Activo", variable=self.estado_var, 
                       onvalue=1, offvalue=0).grid(row=3, column=1, padx=10, pady=8, sticky='w')

        # Campo de contraseña (solo para nuevos usuarios)
        self.pwd_label = ctk.CTkLabel(form_frame, text="Contraseña:", width=100)
        self.pwd_label.grid(row=4, column=0, padx=10, pady=8, sticky='w')
        self.pwd_entry = ctk.CTkEntry(form_frame, show="*", height=35)
        self.pwd_entry.grid(row=4, column=1, padx=10, pady=8, sticky='ew')

        # Botones de acción
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=1, column=0, sticky='e', padx=15, pady=(0, 10))
        
        ctk.CTkButton(btn_frame, text="💾 Guardar", command=self.save_admin,
                     fg_color="#00C853", hover_color="#00A040", width=120).pack(side='left', padx=5)
        
        self.btn_change_pwd = ctk.CTkButton(btn_frame, text="🔑 Cambiar Contraseña", 
                                            command=self.change_password,
                                            fg_color="#FF9800", hover_color="#F57C00", 
                                            width=160, state="disabled")
        self.btn_change_pwd.pack(side='left', padx=5)
        
        ctk.CTkButton(btn_frame, text="🗑️ Eliminar", command=self.delete_admin,
                     fg_color="#F44336", hover_color="#D32F2F", width=120).pack(side='left', padx=5)
        
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.clear_form,
                     fg_color="#607D8B", hover_color="#455A64", width=120).pack(side='left', padx=5)

        # Contenedor de la tabla
        table_container = ctk.CTkFrame(self)
        table_container.grid(row=2, column=0, sticky='nsew', padx=15, pady=(0, 15))
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        # Treeview
        cols = ('id', 'usuario', 'nombre', 'rol', 'estado')
        self.tree = ttk.Treeview(table_container, columns=cols, show='headings')
        
        # Configurar columnas
        self.tree.heading('id', text='ID')
        self.tree.heading('usuario', text='Usuario')
        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('rol', text='Rol')
        self.tree.heading('estado', text='Estado')
        
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('usuario', width=150)
        self.tree.column('nombre', width=200)
        self.tree.column('rol', width=120, anchor='center')
        self.tree.column('estado', width=80, anchor='center')
        
        self.tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        # Scrollbar
        vsb = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.bind('<<TreeviewSelect>>', self.item_selected)
    
    def load_admins(self):
        """Carga todos los administradores desde la API."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        try:
            admins = self.api_client.get_admins()
            
            for admin in admins:
                estado_text = "Activo" if admin['estado'] else "Inactivo"
                self.tree.insert('', 'end', values=(
                    admin['id_admin'], 
                    admin['usuario'], 
                    admin['nombre'], 
                    admin['rol'], 
                    estado_text
                ))
        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "conexión" in error_msg.lower():
                messagebox.showerror("Error de Conexión", f"No se pudo conectar con el servidor: {error_msg}")
            else:
                messagebox.showerror("Error DB", f"Error al cargar administradores: {error_msg}")

    def clear_form(self):
        """Limpia todos los campos del formulario."""
        self.id_var.set('')
        self.usuario_var.set('')
        self.nombre_var.set('')
        self.rol_var.set(self.roles_list[0])
        self.estado_var.set(1)
        self.pwd_entry.delete(0, 'end')
        
        # Mostrar campo de contraseña
        self.pwd_label.grid(row=4, column=0, padx=10, pady=8, sticky='w')
        self.pwd_entry.grid(row=4, column=1, padx=10, pady=8, sticky='ew')
        self.pwd_entry.configure(state='normal')
        
        # Deshabilitar botón de cambiar contraseña
        self.btn_change_pwd.configure(state="disabled")

    def item_selected(self, event):
        """Maneja la selección de un elemento en el Treeview."""
        selection = self.tree.selection()
        if not selection:
            return
        
        self.clear_form()
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        if len(values) >= 5:
            # Cargar datos en el formulario
            self.id_var.set(str(values[0]) if values[0] else '')
            self.usuario_var.set(str(values[1]) if values[1] else '')
            self.nombre_var.set(str(values[2]) if values[2] else '')
            
            # Validar que el rol esté en la lista
            rol_value = str(values[3]) if values[3] else self.roles_list[0]
            if rol_value in self.roles_list:
                self.rol_var.set(rol_value)
            else:
                self.rol_var.set(self.roles_list[0])
            
            # Estado
            estado_text = str(values[4])
            self.estado_var.set(1 if estado_text == "Activo" else 0)
            
            # Ocultar campo de contraseña al editar
            self.pwd_label.grid_forget()
            self.pwd_entry.grid_forget()
            
            # Habilitar botón de cambiar contraseña
            self.btn_change_pwd.configure(state="normal")

    def save_admin(self):
        """Guarda o actualiza un administrador usando la API."""
        usuario = self.usuario_var.get().strip()
        nombre = self.nombre_var.get().strip()
        rol = self.rol_var.get().strip()
        estado = self.estado_var.get()
        
        if not all([usuario, nombre, rol]):
            messagebox.showwarning('Campos Incompletos', 'Usuario, Nombre y Rol son obligatorios')
            return

        try:
            admin_id = self.id_var.get()
            
            if admin_id:
                # Actualizar administrador existente
                admin_data = {
                    "usuario": usuario,
                    "nombre": nombre,
                    "rol": rol,
                    "estado": bool(estado)
                }
                self.api_client.update_admin(int(admin_id), admin_data)
                messagebox.showinfo('Éxito', 'Administrador actualizado correctamente')
            else:
                # Crear nuevo administrador
                password = self.pwd_entry.get().strip()
                if not password:
                    messagebox.showwarning('Contraseña Requerida', 
                                         'La contraseña es obligatoria para un nuevo administrador')
                    return
                
                admin_data = {
                    "usuario": usuario,
                    "nombre": nombre,
                    "rol": rol,
                    "clave": password,
                    "estado": bool(estado)
                }
                self.api_client.create_admin(admin_data)
                messagebox.showinfo('Éxito', 'Administrador agregado correctamente')
            
            self.load_admins()
            self.clear_form()
            
        except Exception as e:
            error_msg = str(e)
            if "ya existe" in error_msg.lower() or "usuario" in error_msg.lower():
                messagebox.showerror('Error', f'El nombre de usuario ya existe')
            elif "connection" in error_msg.lower() or "conexión" in error_msg.lower():
                messagebox.showerror('Error de Conexión', f'No se pudo conectar con el servidor: {error_msg}')
            else:
                messagebox.showerror('Error', f'Error al guardar el administrador: {error_msg}')

    def change_password(self):
        """Cambia la contraseña de un administrador existente usando la API."""
        if not self.id_var.get():
            messagebox.showwarning('Advertencia', 'Seleccione un administrador para cambiar su contraseña')
            return
        
        admin_id = int(self.id_var.get())
        admin_nombre = self.nombre_var.get()
        
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Cambiar Contraseña")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text=f"Cambiar contraseña de: {admin_nombre}", 
                    font=('Segoe UI', 14, 'bold')).pack(pady=20)
        
        # Campo de nueva contraseña
        ctk.CTkLabel(dialog, text="Nueva Contraseña:").pack(pady=5)
        new_pwd_entry = ctk.CTkEntry(dialog, show="*", width=300, height=35)
        new_pwd_entry.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Confirmar Contraseña:").pack(pady=5)
        confirm_pwd_entry = ctk.CTkEntry(dialog, show="*", width=300, height=35)
        confirm_pwd_entry.pack(pady=5)
        
        def save_new_password():
            new_pwd = new_pwd_entry.get().strip()
            confirm_pwd = confirm_pwd_entry.get().strip()
            
            if not new_pwd:
                messagebox.showwarning('Campo Vacío', 'Ingrese la nueva contraseña', parent=dialog)
                return
            
            if new_pwd != confirm_pwd:
                messagebox.showerror('Error', 'Las contraseñas no coinciden', parent=dialog)
                return
            
            try:
                self.api_client.change_admin_password(admin_id, new_pwd)
                messagebox.showinfo('Éxito', 'Contraseña cambiada correctamente', parent=dialog)
                dialog.destroy()
            except Exception as e:
                error_msg = str(e)
                if "connection" in error_msg.lower() or "conexión" in error_msg.lower():
                    messagebox.showerror('Error de Conexión', f'No se pudo conectar con el servidor: {error_msg}', parent=dialog)
                else:
                    messagebox.showerror('Error', f'Error al cambiar contraseña: {error_msg}', parent=dialog)
        
        # Botones
        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar", command=save_new_password,
                     fg_color="#00C853", hover_color="#00A040").pack(side='left', padx=10)
        ctk.CTkButton(btn_frame, text="❌ Cancelar", command=dialog.destroy,
                     fg_color="#F44336", hover_color="#D32F2F").pack(side='left', padx=10)

    def delete_admin(self):
        """Elimina un administrador usando la API."""
        if not self.id_var.get():
            messagebox.showwarning('Advertencia', 'Seleccione un administrador para eliminar')
            return
        
        admin_id = int(self.id_var.get())
        
        # Evitar que el usuario se elimine a sí mismo
        if admin_id == self.current_user.get('IdAdmin'):
            messagebox.showwarning('Error', 'No puedes eliminarte a ti mismo')
            return
        
        if not messagebox.askyesno('Confirmar Eliminación', 
                                   f'¿Está seguro de eliminar al administrador "{self.nombre_var.get()}"?'):
            return
        
        try:
            self.api_client.delete_admin(admin_id)
            messagebox.showinfo('Éxito', 'Administrador eliminado correctamente')
            self.load_admins()
            self.clear_form()
        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "conexión" in error_msg.lower():
                messagebox.showerror('Error de Conexión', f'No se pudo conectar con el servidor: {error_msg}')
            else:
                messagebox.showerror('Error', f'Error al eliminar el administrador: {error_msg}')

