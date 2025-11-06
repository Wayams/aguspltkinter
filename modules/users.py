# frontend/modules/users.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from api_client import APIClient
import re

class UsersWindow(ctk.CTkFrame):
    def __init__(self, master, api_client: APIClient):
        super().__init__(master)
        self.api_client = api_client
        self.selected_user_id = None
        self.build_ui()
        self.configure_treeview_style()
        self.load_users()

    def configure_treeview_style(self):
        """Configura el estilo visual de la tabla (Treeview) de Tkinter."""
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

        if hasattr(self, 'tree'):
            self.tree.tag_configure('Activo', foreground='white') 
            self.tree.tag_configure('Inactivo', foreground='gray')

    def build_ui(self):
        self.columnconfigure(0, weight=1)    
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        
        INPUT_WIDTH = 200

        form_container_frame = ctk.CTkFrame(self)
        form_container_frame.grid(row=0, column=0, sticky='ew', padx=15, pady=(15, 10)) 
        form_container_frame.columnconfigure(0, weight=1) 
        
        title_label = ctk.CTkLabel(form_container_frame, text='Gestión de Suscriptores', font=('Segoe UI', 18, 'bold'), anchor='w')
        title_label.grid(row=0, column=0, sticky='w', padx=15, pady=(10, 10))
        title_label.configure(text_color="#050504") 

        form_content_frame = ctk.CTkFrame(form_container_frame, fg_color='transparent')
        form_content_frame.grid(row=1, column=0, sticky='ew', padx=15, pady=(0, 15)) 
        
        form_content_frame.columnconfigure((0, 1, 2), weight=1)
        form_content_frame.columnconfigure(3, weight=0)
        
        labels = [
            'Nombre:', 'Apellido:', 'Dirección:', 
            'Teléfono:', 'N° Paja:', 'Estado:'
        ]
        self.vars = {}
        
        row_idx = 0
        col_idx = 0
        for text in labels:
            key = text.replace(':', '').replace('N° ', 'Numero')
            
            input_pair_frame = ctk.CTkFrame(form_content_frame, fg_color='transparent')
            input_pair_frame.grid(row=row_idx, column=col_idx, sticky='ew', padx=10, pady=10)
            input_pair_frame.columnconfigure(0, weight=1)
            
            ctk.CTkLabel(input_pair_frame, text=text, anchor='w', font=('Segoe UI', 11, 'bold')).grid(row=0, column=0, sticky='w')
            
            if key == 'Estado':
                self.estado_var = ctk.StringVar(value='Activo')
                self.estado_combobox = ctk.CTkComboBox(input_pair_frame, values=['Activo', 'Inactivo'], variable=self.estado_var, state='readonly', width=INPUT_WIDTH)
                self.estado_combobox.grid(row=1, column=0, sticky='ew')
            else:
                var = ctk.StringVar()
                entry = ctk.CTkEntry(input_pair_frame, textvariable=var, width=INPUT_WIDTH)
                self.vars[key] = var
                entry.grid(row=1, column=0, sticky='ew')
            
            col_idx += 1 
            if col_idx >= 3:
                col_idx = 0
                row_idx = 1
        
        btn_container_frame = ctk.CTkFrame(form_content_frame, fg_color='transparent')
        btn_container_frame.grid(row=0, column=3, rowspan=2, sticky='nsew', padx=15, pady=5)
        btn_container_frame.columnconfigure(0, weight=1) 
        btn_container_frame.rowconfigure((0, 1, 2), weight=1) 

        self.save_btn = ctk.CTkButton(btn_container_frame, 
                                      text='Guardar', 
                                      command=self.save_user,
                                      fg_color='#FFD43B', 
                                      hover_color='#FFD43B',
                                      text_color='black',
                                      height=35) 
        self.save_btn.grid(row=0, column=0, sticky='ew', pady=(10, 8)) 
        
        self.clear_btn = ctk.CTkButton(btn_container_frame, text='Limpiar', command=self.reset_selection, height=35)
        self.clear_btn.grid(row=1, column=0, sticky='ew', pady=8)

        self.deactivate_btn = ctk.CTkButton(btn_container_frame, 
                                            text='Activar/Desactivar', 
                                            command=self.deactivate_user, 
                                            fg_color='#e74c3c', 
                                            hover_color='#c0392b', 
                                            state=ctk.DISABLED,
                                            height=35)
        self.deactivate_btn.grid(row=2, column=0, sticky='ew', pady=(8, 10))

        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=1, column=0, sticky='nsew', padx=15, pady=(5, 15)) 
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1) 

        # Frame para el título y botones de acción
        header_frame = ctk.CTkFrame(list_frame, fg_color='transparent')
        header_frame.grid(row=0, column=0, sticky='ew', padx=15, pady=(10, 10))
        header_frame.columnconfigure(0, weight=1)
        header_frame.columnconfigure(1, weight=0)
        
        ctk.CTkLabel(header_frame, text='Registro de Suscriptores', font=('Segoe UI', 16, 'bold')).grid(row=0, column=0, sticky='w')
        
        # Botones de acción
        buttons_frame = ctk.CTkFrame(header_frame, fg_color='transparent')
        buttons_frame.grid(row=0, column=1, sticky='e', padx=(10, 0))
        
        self.reload_btn = ctk.CTkButton(buttons_frame, 
                                        text='🔄 Recargar', 
                                        command=self.load_users,
                                        fg_color='#3A7CB1', 
                                        hover_color='#2F6593',
                                        width=120,
                                        height=30)
        self.reload_btn.grid(row=0, column=0, padx=5)
        
        tree_frame = ctk.CTkFrame(list_frame)
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=15, pady=(0, 15))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        scrollbar = ctk.CTkScrollbar(tree_frame)
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.tree = ttk.Treeview(tree_frame, columns=('ID', 'Nombre', 'Apellido', 'Direccion', 'Telefono', 'NumPaja', 'Estado'), show='headings', yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.tree.yview)

        self.tree.heading('ID', text='ID', anchor='center')
        self.tree.heading('Nombre', text='Nombre', anchor='center')
        self.tree.heading('Apellido', text='Apellido', anchor='center')
        self.tree.heading('Direccion', text='Dirección', anchor='center')
        self.tree.heading('Telefono', text='Teléfono', anchor='center')
        self.tree.heading('NumPaja', text='N° Paja', anchor='center')
        self.tree.heading('Estado', text='Estado', anchor='center')
        
        self.tree.column('ID', width=50, anchor='center', stretch=ctk.NO)
        self.tree.column('Nombre', width=120, anchor='w')
        self.tree.column('Apellido', width=120, anchor='w')
        self.tree.column('Direccion', width=200, anchor='w')
        self.tree.column('Telefono', width=100, anchor='center')
        self.tree.column('NumPaja', width=80, anchor='center')
        self.tree.column('Estado', width=80, anchor='center')

        self.tree.bind('<<TreeviewSelect>>', self.select_user)
        self.tree.grid(row=0, column=0, sticky='nsew')
        
    def validate_input(self):
        """Valida que los campos sean correctos."""
        nombre = self.vars['Nombre'].get().strip()
        apellido = self.vars['Apellido'].get().strip()
        telefono = self.vars['Teléfono'].get().strip()
        num_paja_str = self.vars['NumeroPaja'].get().strip()
        
        if not nombre or not apellido:
            messagebox.showwarning('Validación', 'Los campos **Nombre** y **Apellido** son obligatorios.')
            return False
            
        phone_pattern = re.compile(r'^(\d{8}|\d{4}-\d{4})$')
        if telefono and not phone_pattern.match(telefono):
            messagebox.showwarning('Validación', 'El **Teléfono** debe tener 8 dígitos (ej. 12345678) o el formato 1234-1234.')
            return False
            
        if not num_paja_str.isdigit() or not num_paja_str:
            messagebox.showwarning('Validación', 'El campo **N° Paja** es obligatorio y debe ser un número (solo dígitos).')
            return False
            
        return True

    def save_user(self):
        """Guarda un nuevo usuario o actualiza uno existente usando la API."""
        if not self.validate_input():
            return

        nombre = self.vars['Nombre'].get().strip()
        apellido = self.vars['Apellido'].get().strip()
        direccion = self.vars['Dirección'].get().strip()
        telefono = self.vars['Teléfono'].get().strip()
        num_paja_str = self.vars['NumeroPaja'].get().strip()
        estado = self.estado_var.get() == 'Activo'

        try:
            user_data = {
                "nombre": nombre,
                "apellido": apellido,
                "direccion": direccion,
                "telefono": telefono,
                "numero_paja": num_paja_str,
                "estado": estado
            }

            if self.selected_user_id is None:
                # Crear nuevo usuario
                self.api_client.create_user(user_data)
                messagebox.showinfo('Éxito', 'Suscriptor guardado correctamente.')
            else:
                # Actualizar usuario existente
                self.api_client.update_user(self.selected_user_id, user_data)
                messagebox.showinfo('Éxito', 'Suscriptor actualizado correctamente.')
                self.selected_user_id = None
                
            self.load_users()
            self.reset_selection()
            
        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "conexión" in error_msg.lower():
                messagebox.showerror('Error de Conexión', f'No se pudo conectar con el servidor: {error_msg}')
            else:
                messagebox.showerror('Error', f'Error al guardar/actualizar suscriptor: {error_msg}')

    def load_users(self):
        """Carga todos los usuarios desde la API."""
        # Deshabilitar botón de recarga mientras carga
        if hasattr(self, 'reload_btn'):
            self.reload_btn.configure(state=ctk.DISABLED, text='🔄 Cargando...')
        self.update()
        
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        try:
            users = self.api_client.get_users()

            for user in users:
                id_user = user['id_usuario']
                nombre = user['nombre']
                apellido = user['apellido']
                direccion = user['direccion']
                telefono = user['telefono'] or ''
                num_paja = str(user['numero_paja'])
                estado_int = user['estado']
                
                estado_text = 'Activo' if estado_int else 'Inactivo'
                num_paja_formatted = num_paja.zfill(3)
                
                tag = estado_text 
                self.tree.insert('', ctk.END, values=(id_user, nombre, apellido, direccion, telefono, num_paja_formatted, estado_text), tags=(tag,))
            
            # Rehabilitar botón de recarga
            if hasattr(self, 'reload_btn'):
                self.reload_btn.configure(state=ctk.NORMAL, text='🔄 Recargar')
                
        except Exception as e:
            error_msg = str(e)
            # Rehabilitar botón de recarga en caso de error
            if hasattr(self, 'reload_btn'):
                self.reload_btn.configure(state=ctk.NORMAL, text='🔄 Recargar')
            if "connection" in error_msg.lower() or "conexión" in error_msg.lower():
                messagebox.showerror('Error de Conexión', f'No se pudo conectar con el servidor: {error_msg}')
            else:
                messagebox.showerror('Error', f'Error al cargar suscriptores: {error_msg}')
            
    def select_user(self, event):
        """Carga los datos del usuario seleccionado en el formulario."""
        selected_item_id = self.tree.selection()
        if not selected_item_id:
            return

        self.reset_selection(keep_form_clear=True)
        
        item = self.tree.item(selected_item_id[0])
        values = item['values']
        
        self.selected_user_id = values[0]
        
        self.vars['Nombre'].set(values[1])
        self.vars['Apellido'].set(values[2])
        self.vars['Dirección'].set(values[3])
        self.vars['Teléfono'].set(values[4])
        self.vars['NumeroPaja'].set(values[5])
        self.estado_var.set(values[6])
        
        self.save_btn.configure(text='Actualizar', fg_color='#3A7CB1', hover_color='#2F6593', text_color='white')
        self.deactivate_btn.configure(state=ctk.NORMAL)
        
        current_status = values[6]
        if current_status == 'Activo':
            self.deactivate_btn.configure(text='Desactivar')
        else:
            self.deactivate_btn.configure(text='Reactivar')

    def reset_selection(self, keep_form_clear=False):
        """Limpia la selección del Treeview y resetea el formulario para registrar un nuevo suscriptor."""
        if not keep_form_clear:
            for var in self.vars.values():
                var.set('')
            self.estado_var.set('Activo')
        
        self.selected_user_id = None
        self.tree.selection_remove(self.tree.selection())
        
        self.save_btn.configure(text='Guardar', fg_color='#FFD43B', hover_color='#E0B810', text_color='black')
        self.deactivate_btn.configure(state=ctk.DISABLED, text='Activar/Desactivar')

    def deactivate_user(self):
        """Cambia el estado del usuario seleccionado usando la API."""
        if self.selected_user_id is None:
            messagebox.showwarning('Selección', 'Debes seleccionar un usuario para cambiar su estado.')
            return

        current_status_text = self.estado_var.get()
        action_text = 'Desactivar' if current_status_text == 'Activo' else 'Reactivar'
        
        confirm = messagebox.askyesno(
            f'{action_text} Usuario', 
            f'¿Estás seguro de que quieres {action_text.lower()} a este usuario?\n'
            'Si lo desactivas, ya no aparecerá en la lista para registrar pagos.'
        )

        if not confirm:
            return

        try:
            self.api_client.toggle_user_status(self.selected_user_id)
            messagebox.showinfo('Éxito', f'Usuario {action_text.lower()}do correctamente.')
            self.load_users()
            self.reset_selection()

        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "conexión" in error_msg.lower():
                messagebox.showerror('Error de Conexión', f'No se pudo conectar con el servidor: {error_msg}')
            else:
                messagebox.showerror('Error', f'Error al cambiar estado: {error_msg}')

